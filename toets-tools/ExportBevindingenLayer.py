import arcpy
import os
import zipfile
#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
inputlayer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Feature Layer, Required
ivrinummer = arcpy.GetParameterAsText(1) #Configure parameter: Input, String, Required

def checkIVRIpath(ivrinummer):
    base_outputpath = r"M:\IVRI"
    ivri_path = rf"{base_outputpath}\{ivrinummer}"
    #Bestaat het IVRI-Nummer?
    if os.path.exists(ivri_path) and os.path.isdir(ivri_path):
        #Ja IVRI-nummer en folder bestaat op M-schijf
        arcpy.AddMessage(f"Outputdirectory: {ivri_path}")
        toets_path = rf"{ivri_path}\toets"
        if os.path.exists(toets_path) and os.path.isdir(toets_path):
            writeOutput(toets_path, inputlayer)
        else:
            arcpy.AddMessage(f"Outputdirectory aanmaken {toets_path}")
            os.makedirs(toets_path)
            os.makedirs(rf"{toets_path}\toets_shapefile")
            writeOutput(toets_path, inputlayer)
    #Wanneer M:\IVRI\ivrinr niet bestaat
    else:
        arcpy.AddError(f"IVRI Pad: {ivri_path} bestaat niet")
    
    
def writeOutput(toetspath, inputlayer):
    #Save feature
    arcpy.AddMessage(f"shapefile opslaan")
    shp_outputpath = rf"{toetspath}\toets_shapefile\bevindingen.shp"
    arcpy.management.CopyFeatures(inputlayer, shp_outputpath)
    
    #Make it a zipfile
    arcpy.AddMessage(f"shapefile zippen")
    shp_folder = rf"{toetspath}\toets_shapefile"
    zip_outputpath = rf"{toetspath}\toets_shapefile.zip"
    with zipfile.ZipFile(zip_outputpath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(shp_folder):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, shp_folder)
                zipf.write(abs_file, rel_path)
    
    #Tekstfile schrijven
    arcpy.AddMessage(f"textfile aanmaken")
    kolom1 = "Volgnummer"
    kolom2 = "Fout"
    kolom3 = "Omschrijving"
    kolom4 = "Bijlage_nr"
    txtfile_outputpath = rf"{toetspath}\toets_tekst.txt"
    with open(txtfile_outputpath, "w", encoding="utf-8") as file:
        file.write(f"{kolom1}\t{kolom2}\t{kolom3}\t{kolom4}\n")
        with arcpy.da.SearchCursor(inputlayer, [kolom1, kolom2, kolom3, kolom4]) as cursor:
            for row in cursor:
                volgnummer = row[0] if row[0] is not None else ""
                fout = row[1] if row[1] is not None else ""
                omschrijving = row[2] if row[2] is not None else ""
                bijlage = row[3] if row[3] is not None else ""
                file.write(f"{volgnummer}\t{fout}\t{omschrijving}\t{bijlage}\n")

checkIVRIpath(ivrinummer)