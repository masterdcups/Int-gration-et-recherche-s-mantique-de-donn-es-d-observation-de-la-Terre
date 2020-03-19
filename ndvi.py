#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gdal
import os
import time
import math
import argparse
import rasterio
from shapely.geometry import shape
from rasterio.mask import mask
import geopandas as gpd
from functions import writeToFile, triplify, readTemplate
import pyproj
from shapely.ops import transform
from functools import partial
import numpy as np
from IPython.display import clear_output

templateFile = '../templates/template_NDVI_dept.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 1000000


def triplify_dataset(file, parcel_file, product_id, output_folder='./rdf'):

    startEpoch = time.time()

    files = []
    triples = []
    iFiles = 0
    iTriples = 0
    village = parcel_file[-20:-15]
    lsNameSpaces, lsTriplesTemplate = readTemplate(templateFile)

    ndvi_file = rasterio.open(file)

    print("ndvi_file data read, CRS (expected 32630):", ndvi_file.crs)
    parcelFile = gpd.read_file(parcel_file)
    if '/' in file:
        image_date = file[file.rfind('/') + 1:-7]
    else:
        image_date = file[0:-7]

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init=ndvi_file.crs))

    for index, row in parcelFile.iterrows():
        clear_output()
        print(str(index) + '/' + str(len(parcelFile)))
        feat = {}
        feat['id'] = str(row['id'])
        feat['parcel'] = str(row['id'])
        feat['area_type'] = str(row['area_type'])
        feat['geojson'] = shape(row['geometry']).wkt
        try:
            geom = transform(project, row['geometry'])
            ndviParcel, ndviTransform = mask(
                ndvi_file, [geom], crop=True, all_touched=True, indexes=1)
        except ValueError as err:
            print(err)
            continue
        ndvi = np.float16(ndviParcel)
        total = ndvi[ndvi >= 0.2].size
        if total <= 0:
            try:
                geom = transform(project, row['geometry'])
                ndviParcel, ndviTransform = mask(
                    ndvi_file, [geom], crop=True, indexes=1)
            except ValueError as err:
                print(err)
                continue
        ndvi = np.float16(ndviParcel)
        total = ndvi[ndvi >= 0.2].size
        if total > 0:
            feat['lowp'] = round(
                ndvi[(ndvi >= 0.2) & (ndvi < 0.5)].size * 100 / total, 2)
            feat['midp'] = round(
                ndvi[(ndvi >= 0.5) & (ndvi < 0.7)].size * 100 / total, 2)
            feat['highp'] = round(ndvi[(ndvi >= 0.7)].size * 100 / total, 2)

            feat['id'] = "PN" + feat['id'] + "_" + image_date
            feat['id'] = feat['id'].replace('-', '_')

            feat['image'] = product_id
            uriDummy = URIBase + 'NDVI/' + feat['id'] + ">"
            triplesRow = triplify(feat, lsTriplesTemplate, uriDummy, feat['id'], feat['parcel'])

            triples = triples + triplesRow
            if len(triples) > maxRecordsPerFile:
                file = output_folder
                files.append(file)
                writeToFile(lsNameSpaces, triples, file)
                iFiles = iFiles + 1
                iTriples = iTriples + len(triples)
                triples = []
        else:
            print("Too small!")

    file = output_folder + 'ndvi.ttl'
    writeToFile(lsNameSpaces, triples, file)

    files.append(file)
    clear_output()
    print('Number of parcel', len(parcelFile))
    print('Number of triples', iTriples)
    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch
    if elapsedTime < 60:
        print('Elapsed time : ', elapsedTime, ' seconds')
    else:
        print('Elapsed time : ', math.floor(elapsedTime / 60),
              ' minutes and ', elapsedTime % 60, ' seconds')
    return files
