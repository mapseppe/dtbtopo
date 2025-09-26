import arcpy
import os
import zipfile
import shutil
import openpyxl
from openpyxl.utils import coordinate_to_tuple
#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
inputlayer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Feature Layer, Required
ivrinummer = arcpy.GetParameterAsText(1) #Configure parameter: Input, String, Required
rapportnaam = arcpy.GetParameterAsText(2) #Configure parameter: Input, String, Required
templatesheet = arcpy.GetParameterAsText(3) #Configure parameter: Input, File, Optional
tempsave = arcpy.GetParameterAsText(4) #Configure parameter: Input, Boolean, Required, Default"False"

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
    #Sorteer op fouttype
    sortedlayer = arcpy.management.Sort(inputlayer, "in_memory\sort", [["Fout", "ASCENDING"]])
    
    #Vul X en Y coördinaten in
    arcpy.management.CalculateGeometryAttributes(sortedlayer, [["xcoord", "POINT_X"],
                                                              ["ycoord", "POINT_Y"]])
    
    #Save feature (alles)
    arcpy.AddMessage(f"totaal-shapefile opslaan")
    shp_outputpath = rf"{toetspath}\toets_totaal\bevindingen-totaal.shp"
    arcpy.management.CopyFeatures(sortedlayer, shp_outputpath)
    
    #Stel naamgeving in
    arcpy.AddMessage(f"on-shapefile opslaan")
    toetsnr = 0
    toetssfx = ""
    if tempsave == "true":
        toetssfx = "_concept"
    else:
        while os.path.exists(rf"{toetspath}\toets_on{toetssfx}"):
            toetsnr += 1
            toetssfx = f"_{toetsnr}"
    toetspath_on = rf"{toetspath}\toets_on{toetssfx}"
    
    #Save feature met 'Zichtbaar = Ja'
    os.makedirs(toetspath_on)
    shapepath_on = rf"{toetspath_on}\bevindingen.shp"
    arcpy.AddMessage(f"Volgnummers toepassen")
    volgnr = 1
    with arcpy.da.UpdateCursor(sortedlayer, ["Volgnummer"], '"Zichtbaar" = \'Ja\'') as cursor:
        for row in cursor:
            row[0] = volgnr
            cursor.updateRow(row)
            volgnr += 1
    zichtbaarlayer = arcpy.management.SelectLayerByAttribute(sortedlayer, "NEW_SELECTION", '"Zichtbaar" = \'Ja\'')
    onlayer = arcpy.management.CopyFeatures(zichtbaarlayer, shapepath_on)
    arcpy.management.DeleteField(onlayer, ["Zichtbaar","Voorkomen", "ORIG_FID"])
    
    #Make it a zipfile
    arcpy.AddMessage(f"shapefile zippen")
    shp_folder = rf"{toetspath}\toets_on{toetssfx}"
    zip_outputpath = rf"{toetspath}\bevindingen_shapefile{toetssfx}.zip"
    with zipfile.ZipFile(zip_outputpath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(shp_folder):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, shp_folder)
                zipf.write(abs_file, rel_path)

    #beoordelingsrapport kopiëren
    arcpy.AddMessage(f"Beoordelingsrapport kopiëren")
    if templatesheet != "":
        standard_rapport = templatesheet
    else:
        standard_rapport = rf"G:\civ\IGA_ATG\Producten\DTB\Toetstooling\beoordelingsrapport_template\beoordelingsrapport_dtb.xlsm"
    rapport_loc = rf"{toetspath}\{rapportnaam}{toetssfx}.xlsm"
    shutil.copy2(standard_rapport, rapport_loc)
    excel = openpyxl.load_workbook(rapport_loc, keep_vba=True)
    excelsheet = excel["Beoordelingsrapport"]
    
    #standaardcellen, moet overeenkomen met de 'invulvelden.txt' van het dropdownmenu/domein
    vraag_cel_map = {
        "6.3 Hier wordt niet voldaan aan de eisen gesteld aan de bestandsopbouw": "C91",
        "6.4 Hier wordt niet voldaan aan de eisen gesteld aan de attribuutwaarden": "C98",
        "6.5 Hier sluit het nieuwe DTB niet goed aan op het oude DTB": "C105",
        "6.6 Hier wordt niet voldaan aan de eisen gesteld aan de inwinning van objecten": "C112",
        "6.7 Hier wordt niet voldaan aan de eisen gesteld aan de volledigheid": "C119",
        "6.8 Hier wordt niet voldaan aan de eisen gesteld aan de meetpunten": "C126"
    }
    
    #schrijf een standaardtekst in de cel voor elke shape
    arcpy.AddMessage(f"Beoordelingsrapport vullen")
    kolom1 = "Volgnummer"
    kolom2 = "Fout"
    kolom3 = "Omschrijvi"
    kolom4 = "Bijlage_nr"
    kolom5 = "Voorkomen"
    kolom6 = "xcoord"
    kolom7 = "ycoord"
    with arcpy.da.SearchCursor(zichtbaarlayer, [kolom1, kolom2, kolom3, kolom4, kolom5, kolom6, kolom7]) as cursor:
            for row in cursor:
                
                #lees attributentabel en vertaal naar veriabelen
                volgnummer = row[0] if row[0] is not None else ""
                fout = row[1] if row[1] is not None else ""
                omschrijving = row[2] if row[2] is not None else ""
                bijlage = row[3] if row[3] is not None else ""
                if bijlage == "":
                    bijlagetxt = ""
                else:
                    bijlagetxt = f"Zie bijlage {bijlage}.\n"
                voorkomen = row[4] if row[4] is not None else ""
                if voorkomen == "Eenmalig":
                    voorkomentxt = ""
                elif voorkomen == "Meermalig":
                    voorkomentxt = f"Deze situatie komt vaker voor in het geleverde DTB-bestand.\n"
                xcoord = row[5] if row[5] is not None else ""
                ycoord = row[6] if row[6] is not None else ""
                
                #maak er een volledig stuk standaardtekst van
                fulltext = (
                    f"\n"
                    f"Zie volgnummer {volgnummer} in het meegestuurde shapefile bestand, "
                    f"ter plaatse van x={xcoord}, y={ycoord}.\n"
                    f"{omschrijving}\n"
                    f"{voorkomentxt}"
                    f"{bijlagetxt}"
                    "--------------------------------"
                )
                
                #voeg het toe in de besbetreffende cel
                targetcell = vraag_cel_map.get(fout)
                cellvalue = excelsheet[targetcell].value
                if cellvalue is None:
                    cellvalue = ""
                newcellvalue = cellvalue + fulltext
                excelsheet[targetcell] = newcellvalue
                
                #verander de row height van de cel
                rownumber = coordinate_to_tuple(targetcell)[0]
                currentrowh = excelsheet.row_dimensions[rownumber].height
                excelsheet.row_dimensions[rownumber].height = currentrowh + 100
                
                fout_bevinding_map = {"C91":"M90","C98":"M97","C105":"M104","C112":"M111","C119":"M118","C126":"M125"}
                for c_cell, m_cell in fout_bevinding_map.items():
                    c_value = excelsheet[c_cell].value
                    if c_value is None:
                        excelsheet[m_cell].value = "Ja"
                    else:
                        excelsheet[m_cell].value = "Nee"
                    rownumber2 = coordinate_to_tuple(m_cell)[0]
                    excelsheet.row_dimensions[rownumber2].height = 35
                
    excel.save(rapport_loc)

checkIVRIpath(ivrinummer)