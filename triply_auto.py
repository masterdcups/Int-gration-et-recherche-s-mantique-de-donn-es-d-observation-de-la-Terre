import land_cover as lc
import ndvi
import change as ch
import change2 as ch2
import upload_local as ul

# Initialiser avec le chemin absolu de votre projet

server = ""


def triplify_auto(parcel_file, ndvi_file, landCover_file, change_file, change_file2, result_folder):
    numChange1 = 0
    numChange2 = 0
    numLC = 0
    numNDVI = 0

    if parcel_file is not None:
        for i in parcel_file:
            if landCover_file is not None:
                for j in landCover_file:
                    lc.triplify_dataset(j, i, result_folder + str(numLC))
                    numLC += 1
            if change_file is not None:
                for j in change_file:
                    ch.triplify_dataset(j, i, result_folder + str(numChange1))
                    numChange1 += 1
            if change_file2 is not None:
                for j2 in change_file2:
                    ch2.triplify_dataset(j2, i, result_folder + str(numChange2))
                    numChange2 += 1
            if ndvi_file is not None:
                for j in ndvi_file:
                    ndvi.triplify_dataset(j, i, '1', result_folder + str(numNDVI))
                    numNDVI += 1

    ul.upload_dataset(result_folder, server, 'http://localhost:8080/strabon-endpoint-3.3.2-SNAPSHOT/Store', 'endpoint')

parcel_files = ["../../data/G_SUBAREA2.shp"]
landCover_files = ["../../data/test.tif"]
ndvi_files = ["../../data/ndvi_34UCD_20170730.tiff", "../../data/ndvi_34UCD_20170829.tiff"]
change_files = ["../../data/result_L2A_T34UCD_20170730T100031.tif"]
change_files2 = ["../../data/S1B_S1B_GRDH_1SVV_20170805_20170817_CD_KMEANS_SNGL.tif", "../../data/S1B_S1B_GRDH_1SVV_20170805_20170817_CD_SPECT_SNGL.tif"]

triply_auto(parcel_files, ndvi_files, landCover_files, change_files, change_files2, "../../result")
