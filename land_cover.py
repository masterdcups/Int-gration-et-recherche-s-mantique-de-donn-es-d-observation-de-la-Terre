#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import math
import argparse
from shapely.geometry import shape
from shapely import wkt
import pandas as pd
import geopandas as gpd
import rasterio
import numpy as np
import pyproj
from shapely.ops import transform
from functools import partial
from collections import Counter
from rasterio.mask import mask
from functions import writeToFile, triplify, readTemplate
from IPython.display import clear_output

templateFile = '../templates/template_Parcel_forest.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 100000


def correspond_land_cover(num) :
    df = pd.read_csv('land_cover.csv', header=None, index_col=0)
    for index, row in df.iterrows():
        if index == num:
            return row[5]
    print("pas de land_cover correspondant")
    return ""


def triplify_dataset(cesbio_file, parcel_file, output_folder):
    startEpoch = time.time()
    print('triplify Cadastral parcel and its land-cover')
    village = parcel_file[-20:-15]
    triples = []
    files = []
    iFiles = 0
    iTriples = 0
    lsNameSpaces, lsTriplesTemplate = readTemplate(templateFile)
    CesbioFile = rasterio.open(cesbio_file)
    print("Land cover (expected 4326):", CesbioFile.crs)
    parcelFile = gpd.read_file(parcel_file)

    print(CesbioFile.crs)
    if '.shp' in parcel_file:
        project = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'),
                pyproj.Proj(init='epsg:4326'))



    for index, row in parcelFile.iterrows():
        clear_output()
        print(str(index) + '/' + str(len(parcelFile)))
        feat = {}
        feat['id'] = row['id']
        feat['geojson'] = shape(row['geometry']).wkt
        try:
            geom = transform(project, row['geometry'])
            LCParcel, LCTransform = mask(CesbioFile, [geom], crop=True, indexes=1, nodata=0) 
        except ValueError as err:
            print(err)
            continue

        if np.count_nonzero(LCParcel) <= 0:
            try:
                geom = transform(project, row['geometry'])
                LCParcel, LCTransform = mask(CesbioFile, [geom], crop=True, all_touched=True, indexes=1, nodata=0)
            except ValueError as err:
                print(err)
                continue
            
        if np.count_nonzero(LCParcel) > 0:
            counter = Counter(LCParcel.ravel())
            dominantLCCode, DominantLCFreq = counter.most_common(2)[0]
            if dominantLCCode == 0:
                dominantLCCode, DominantLCFreq = counter.most_common(2)[1]

            percentage = round(DominantLCFreq * 100 / np.count_nonzero(LCParcel), 0)
            feat['lc'] = correspond_land_cover(dominantLCCode)
            URI = URIBase + 'Parcel/' + str(row['id']) + ">"
            triplesRow = triplify(feat, lsTriplesTemplate, URI, "p" + str(row['id']))
            triples = triples + triplesRow
        else:
            print("Too small!")

    file = output_folder + 'land_cover.ttl'
    files.append(file)
    writeToFile(lsNameSpaces, triples, file)
    clear_output()
    print('Number of triples', iTriples)
    print('Number of parcel', len(parcelFile))
    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch

    if elapsedTime < 60:
        print('Elapsed time : ', elapsedTime, ' seconds')
    else:
        print('Elapsed time : ', math.floor(elapsedTime / 60), ' minutes and ', elapsedTime % 60, ' seconds')
    return files
