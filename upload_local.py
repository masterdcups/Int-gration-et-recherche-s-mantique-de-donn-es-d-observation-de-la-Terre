import argparse
from os import listdir
from os.path import isfile, isdir, join, abspath, splitext, getsize, basename
import requests
import sys
import time
import math
import getpass
from requests.auth import HTTPBasicAuth
from rdflib import Graph

def uploadFile(lfile, sfile, url, login, pwd): #validate localfile, upload the corresponding serverfile
    print(sfile)
    r = requests.post(url, data={
                'format':'Turtle',
                'view':'HTML',
                'fromurl':'Store from URI',
                'url': 'file:///' + sfile
                }, auth=(login, pwd), verify=False, timeout=120)

    print("Connection:", r.status_code, r.reason)
    msg= r.text.split("\n")
    rs = msg[162].strip()
    rs = rs[11:-13]

    if "successfully" not in rs:
        print("Result:", msg[160][36:-13])
    else:
        print("Result:", rs)

def upload_dataset(input_file, server_path, endpoint, login):
    print("Please upload the folder to the server before excuting the script")
    startEpoch = time.time()
    #url = 'https://185.178.85.62/semsearch/ep/Store'
    #url = 'http://melodi.irit.fr/ep/Store'
    pwd = ""
    try:
        print("Enter endpoint password")
        pwd = getpass.getpass()
    except Exception as error:
        pwd = 'melodi'
        print('ERROR', error)
        print('Use default password')


    if isfile(input_file):
        uploadFile(input_file, server_path + basename(input_file), endpoint, login, pwd )
    else:
        print("Folder")
        for f in listdir(input_file):
            stFile = join(input_file, f)
            if isfile(stFile):
                if splitext(stFile)[1] == ".ttl":
                    uploadFile(input_file + f, server_path + f, endpoint, login, pwd )
                    time.sleep(5)


    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch
    if elapsedTime < 60:
        print('Elapsed time : ', elapsedTime, ' seconds')
    else:
        print('Elapsed time : ', math.floor(elapsedTime / 60), ' minutes and ', elapsedTime % 60, ' seconds' )



#upload_dataset('dat_ndvi_34UCD_201707_0.ttl', 'C:/Users/sebas/Downloads/', 'http://localhost:8080/strabon-endpoint-3.3.2-SNAPSHOT/Store', 'endpoint' )
