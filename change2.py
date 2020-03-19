import time
import math
import argparse
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from functions import writeToFile, triplify, readTemplate
import pyproj
from shapely.ops import transform
from functools import partial
import numpy as np
from IPython.display import clear_output

templateFile = '../templates/template_Change_dept.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 50000


def triplify_dataset(change_file, parcel_file,  output_folder):
    startEpoch = time.time()    
    files = []
    print('Compute and triplify change detection result')
    village = parcel_file[-20:-15]
    triples = []
    iFiles = 0
    iTriples = 0
    lsNameSpaces, lsTriplesTemplate = readTemplate(templateFile)
    changeFile = rasterio.open(change_file)   
    print("Change data read, CRS (expected 32630):", changeFile.crs)
    img1 = changeFile.tags()['T1_Product_ID']
    img2 = changeFile.tags()['T2_Product_ID']
    start_date = changeFile.tags()['T1_Start_Date']
    end_date = changeFile.tags()['T2_Start_Date']
    parcelFile = gpd.read_file(parcel_file)  
    if '.shp' in parcel_file:
        project = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'),
                pyproj.Proj(init=changeFile.crs))

    for index, row in parcelFile.iterrows():
        clear_output()
        print(str(index) + '/' + str(len(parcelFile)))
        feat = {}
        feat['id'] = row['id']
        feat['parcel'] = row['id']
        try:           
            geom = transform(project, row['geometry'])
            parcelChange, changeTransform = mask(changeFile, [geom], crop=True, indexes=1, nodata=-1)
        except ValueError as err:
            print(err)
            continue

        total = parcelChange[parcelChange>=0].size
        if total <= 0:
            try:
                geom = transform(project, row['geometry'])
                parcelChange, changeTransform = mask(changeFile, [geom], crop=True, all_touched=True, indexes=1, nodata=-1)
            except ValueError as err:
                print(err)
                continue

        if total > 0:
            feat['nop'] = round(parcelChange[(parcelChange < 0.1) & (parcelChange >= 0)].size*100/total,2)
            feat['lowp'] = round(parcelChange[(parcelChange >= 0.1) & (parcelChange < 0.4)].size*100/total,2)
            feat['midp'] = round(parcelChange[(parcelChange >= 0.4) & (parcelChange < 0.7)].size*100/total,2)
            feat['highp'] = round(parcelChange[(parcelChange >= 0.7)].size*100/total,2)
            feat['id'] = "PC" + str(feat['id']) + "_" + start_date + "_" + end_date
            feat['id'] = str(feat['id']).replace('-','_')
            feat['image1'] = img1
            feat['image2'] = img2
            uriDummy = URIBase + 'Change/' + str(feat['id'])+">"
            triplesRow = triplify(feat, lsTriplesTemplate,
                                  uriDummy, str(feat['id']), str(feat['parcel']))

            triples = triples + triplesRow

        else:
            print("no data on this parcel")

    file = output_folder + 'change.ttl'

    files.append(file)
    writeToFile(lsNameSpaces, triples, output_folder)
    clear_output()
    print('Number of triples', iTriples)
    print('Number of parcel', len(parcelFile))
    
    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch
    if elapsedTime < 60:
        print('Elapsed time : ', elapsedTime, ' seconds')
    else:
        print('Elapsed time : ', math.floor(elapsedTime / 60),
              ' minutes and ', elapsedTime % 60, ' seconds')

    return files
