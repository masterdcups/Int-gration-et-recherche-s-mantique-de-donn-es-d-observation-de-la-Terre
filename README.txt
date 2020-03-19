def triplify_auto(parcel_file, ndvi_file, landCover_file, change_file, change_file2, result_folder)


Pour utiliser triplify_auto, il faut mettre les chemins de chaque fichier en paramètre de la fonction

On peut mettre plusieurs fichiers pour chaque type de fichiers, il suffit de passer en paramètre une liste de chemins.

parcel_file: Les fichiers contenant les parcelles
ndvi_file: Les fichiers contenant l'indice de végétation
landCover_file: Les fichiers contenant l'occupation des sols
change_file: Fichiers contenant les resultats de la detection de changement ayant comme attribut: 
(Product_id1, Product_id2, Start_date, End_date)
change_file2: Fichiers contenant les resultats de la recherche de changement ayant comme attribut: 
(T1_Product_ID, T2_Product_ID, T1_Start_Date, T2_Start_Date)
result_folder: chemin du dossier dans lequel seront stockés les RDF

Avant de lancer le programme il faut changer la variable "server" dans triplify_auto par le chemin absolue de 
votre dossier