import arcpy
import os
import zipfile
import shutil
import openpyxl
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
            os.makedirs(rf"{toets_path}\toets_totaal")
            writeOutput(toets_path, inputlayer)
            
    #Wanneer M:\IVRI\ivrinr niet bestaat
    else:
        arcpy.AddError(f"IVRI Pad: {ivri_path} bestaat niet")
    
def writeOutput(toetspath, inputlayer):
    #Vul X en Y coördinaten in
    arcpy.management.CalculateGeometryAttributes(inputlayer, [["xcoord", "POINT_X"],
                                                              ["ycoord", "POINT_Y"]])
    
    #Save feature (alles)
    arcpy.AddMessage(f"totaal-shapefile opslaan")
    shp_outputpath = rf"{toetspath}\toets_totaal\bevindingen-totaal.shp"
    arcpy.management.CopyFeatures(inputlayer, shp_outputpath)
    
    #Save feature met 'Zichtbaar = Ja'
    arcpy.AddMessage(f"on-shapefile opslaan")
    toetsnr = 1
    while os.path.exists(rf"{toetspath}\toets_on_{toetsnr}"):
        toetsnr += 1
    toetspath_on = rf"{toetspath}\toets_on_{toetsnr}"
    os.makedirs(toetspath_on)
    shapepath_on = rf"{toetspath_on}\bevindingen.shp"
    arcpy.management.SelectLayerByAttribute(inputlayer, "NEW_SELECTION", '"Zichtbaar" = \'Ja\'')
    arcpy.management.CopyFeatures(inputlayer, shapepath_on)
    
    #Make it a zipfile
    arcpy.AddMessage(f"shapefile zippen")
    shp_folder = rf"{toetspath}\toets_on_{toetsnr}"
    zip_outputpath = rf"{toetspath}\toets_on_{toetsnr}.zip"
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
    kolom5 = "xcoord"
    kolom6 = "ycoord"
    txtfile_outputpath = rf"{toetspath}\toets_tekst_{toetsnr}.txt"
    with open(txtfile_outputpath, "w", encoding="utf-8") as file:
        with arcpy.da.SearchCursor(inputlayer, [kolom1, kolom2, kolom3, kolom4, kolom5, kolom6]) as cursor:
            for row in cursor:
                volgnummer = row[0] if row[0] is not None else ""
                fout = row[1] if row[1] is not None else ""
                omschrijving = row[2] if row[2] is not None else ""
                bijlage = row[3] if row[3] is not None else ""
                if bijlage == "":
                    bijlagetxt = ""
                else:
                    bijlagetxt = f"Zie bijlage {bijlage}."
                xcoord = row[4] if row[4] is not None else ""
                ycoord = row[5] if row[5] is not None else ""
                file.write(f"Zie volgnummer {volgnummer} in het meegestuurde shapefile bestand, ter plaatse van x={xcoord}, y={ycoord}.\n"
                           + f"{fout}.\n"
                           + f"{omschrijving}\n"
                           + f"{bijlagetxt}\n"
                           + "--------------------------------\n")
                
    #beoordelingsrapport kopiëren
    arcpy.AddMessage(f"Beoordelingsrapport kopiëren")
    standard_rapport = rf"G:\civ\IGA_ATG\Producten\DTB\Toetstooling\beoordelingsrapport_template\beoordelingsrapport_dtb.xlsm"
    rapport_loc = rf"{toetspath}\job{ivrinummer}_beoordelingsrapport_{toetsnr}.xlsm"
    shutil.copy2(standard_rapport, rapport_loc)
    excel = openpyxl.load_workbook(rapport_loc, keep_vba=True)
    excelsheet = excel["Beoordelingsrapport"]
    
    #standaardcellen, moet overeenkomen met de 'invulvelden.txt' van het dropdownmenu/domein
    vraag_cel_map = {
        "Hier wordt niet voldaan aan de eisen gesteld aan de bestandsopbouw": "C91",
        "Hier wordt niet voldaan aan de eisen gesteld aan de attribuutwaarden": "C98",
        "Hier wordt niet voldaan aan de eisen gesteld aan de inwinning van objecten": "C105",
        "Hier sluit het nieuwe DTB niet goed aan op het oude DTB": "C112",
        "Hier wordt niet voldaan aan de eisen gesteld aan de volledigheid": "C119",
        "Hier wordt niet voldaan aan de eisen gesteld aan de meetpunten": "C126"
    }
    
    #schrijf een standaardtekst in de cel voor elke shape
    arcpy.AddMessage(f"Beoordelingsrapport vullen")
    with arcpy.da.SearchCursor(inputlayer, [kolom1, kolom2, kolom3, kolom4, kolom5, kolom6]) as cursor:
            for row in cursor:
                
                #lees attributentabel
                volgnummer = row[0] if row[0] is not None else ""
                fout = row[1] if row[1] is not None else ""
                omschrijving = row[2] if row[2] is not None else ""
                bijlage = row[3] if row[3] is not None else ""
                if bijlage == "":
                    bijlagetxt = ""
                else:
                    bijlagetxt = f"Zie bijlage {bijlage}."
                xcoord = row[4] if row[4] is not None else ""
                ycoord = row[5] if row[5] is not None else ""
                
                #maak er een volledig stuk standaardtekst van
                fulltext = (
                    f"Zie volgnummer {volgnummer} in het meegestuurde shapefile bestand, "
                    f"ter plaatse van x={xcoord}, y={ycoord}.\n"
                    f"{fout}.\n"
                    f"{omschrijving}\n"
                    f"{bijlagetxt}\n"
                    "--------------------------------\n"
                )
                
                #voeg het toe in de besbetreffende cel
                targetcell = vraag_cel_map.get(fout)
                cellvalue = excelsheet[targetcell].value
                if cellvalue is None:
                    cellvalue = ""
                newcellvalue = cellvalue + fulltext
                excelsheet[targetcell] = newcellvalue
    excel.save(rapport_loc)
    
checkIVRIpath(ivrinummer)