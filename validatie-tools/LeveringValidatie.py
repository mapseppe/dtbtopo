import arcpy
import os
import glob
arcpy.env.overwriteOutput = True

#Parameters for inputs and outputs
ivrinummer = arcpy.GetParameterAsText(0) #Input, String
valicheckA = arcpy.GetParameter(1) #Input, Boolean
valicheckB = arcpy.GetParameter(2) #Input, Boolean
valicheckC = arcpy.GetParameter(3) #Input, Boolean
output_punt = arcpy.GetParameterAsText(4) #Output, Derived, Feature Layer, Symbology instellen
output_lijn = arcpy.GetParameterAsText(5) #Output, Derived, Feature Layer, Symbology instellen
output_vlak = arcpy.GetParameterAsText(6) #Output, Derived, Feature Layer, Symbology instellen

#Check if .gdb in IVRI folder exists
ivripath = rf"M:\IVRI\{ivrinummer}"
ivrigdbpath = rf"{ivripath}\levering\temp"
gdb_list = glob.glob(os.path.join(ivrigdbpath, "*.gdb"))
if gdb_list:
    arcpy.AddMessage(f"Start validatie met input: {ivrigdbpath}")
else:
    arcpy.AddError(f"Geen .gdb gevonden in: {ivrigdbpath}")

#Determine the paths of the input.gdb and output.gdb
inputgdb = gdb_list[0]
outputgdb_template = rf"G:\civ\IGA_ATG\Producten\DTB\Toetstooling - AAT Next\template_output\template_output.gdb"
outputpath = rf"M:\IVRI\{ivrinummer}\validatie_output.gdb"

#Create an empty output.gdb to which validation results will be written, unless it already exists
validatiepath = rf"M:\IVRI\{ivrinummer}\validatie_output.gdb"
if os.path.exists(validatiepath) and os.path.isdir(validatiepath):
    arcpy.AddMessage("Validatie_output.gdb bestaat al, validaties worden aan de bestaande toegevoegd")
else:
    arcpy.AddMessage(rf"Nieuwe validatie_output.gdb aanmaken in {ivripath}")
    arcpy.management.Copy(outputgdb_template, outputpath)

#Validatie voor vlakken met dezelfde TYPE & FUNCTIE die naast elkaar liggen op hetzelfde niveau zonder vlakscheidende lijn ertussen
def validatieA(input, output):

    #Merge the vlakkennet
    dtb_path = rf"{input}\DTB_DATA"
    dtb_vlakkennet_list = ["DTB_BEBOUWING_VLAKKEN", "DTB_BEKLEDING_VLAKKEN","DTB_GROND_VLAKKEN", "DTB_INSTALLATIE_VLAKKEN", 
                      "DTB_TERREIN_VLAKKEN", "DTB_VERHARDING_VLAKKEN", "DTB_WATER_VLAKKEN"]
    dtb_vlakkennet_data = [f"{dtb_path}\{item}" for item in dtb_vlakkennet_list]
    dtb_vlakkennet = arcpy.management.Merge(dtb_vlakkennet_data, r"in_memory\vlaknetmerge")
    dtb_id_field = arcpy.Describe(dtb_vlakkennet).OIDFieldName  

    #Go through validation for each NIVEAU
    for niveau in [0, 1, 2, 3]:
        arcpy.AddMessage(rf"Calculating difference for niveau: {niveau}")
        niveausql = rf'"NIVEAU" = {niveau}'
        dtb_vlakkennet_perniveau = arcpy.management.SelectLayerByAttribute(dtb_vlakkennet, "NEW_SELECTION", niveausql)
        dtb_vlakkennet_niveaucount = int(arcpy.management.GetCount(dtb_vlakkennet_perniveau)[0])
        if dtb_vlakkennet_niveaucount < 1:
            arcpy.AddMessage(f"Geen vlakken op niveau {niveau}")
        else:
            arcpy.AddMessage(f"Start validatie voor niveau {niveau}")
            
            #Convert polygon to polygon borders, taking LEFT and RIGHT FID for shared borders
            arcpy.AddMessage("Convert polygonborder naar line")
            polygon_borders = arcpy.management.PolygonToLine(dtb_vlakkennet_perniveau, r"in_memory\polyborders")

            #Join the TYPE and FUNCTIE of the original polygon to the polygon_border
            arcpy.AddMessage("Join TYPE en FUNCTIE van vlakken op gedeelde polygonborder")
            arcpy.management.JoinField(polygon_borders, "LEFT_FID", dtb_vlakkennet_perniveau, dtb_id_field, ["DTB_ID", "TYPE", "FUNCTIE"])
            arcpy.management.JoinField(polygon_borders, "RIGHT_FID", dtb_vlakkennet_perniveau, dtb_id_field, ["DTB_ID", "TYPE", "FUNCTIE"])

            #Filter the shared polygon borders to ones where both polygons are the same TYPE and FUNCTIE
            arcpy.AddMessage("Filter polygonborders op aanliggende polygons met dezelfde TYPE + FUNCTIE")
            sql = "((FUNCTIE = FUNCTIE_1 OR (FUNCTIE IS NULL AND FUNCTIE_1 IS NULL)) AND (TYPE = TYPE_1 OR (TYPE IS NULL AND TYPE_1 IS NULL)))"
            filtered_polyborders = arcpy.management.SelectLayerByAttribute(polygon_borders, "NEW_SELECTION", sql)

            #Remove the ones from selection that are divided by vlak-scheidende-lijnen
            arcpy.AddMessage("Maak uitzondering voor vlakscheidende lijnen")
            scheiding_lijnen = rf"{input}\DTB_DATA\DTB_SCHEIDING_LIJNEN"
            result = arcpy.management.SelectLayerByLocation(filtered_polyborders, "SHARE_A_LINE_SEGMENT_WITH", scheiding_lijnen, selection_type="REMOVE_FROM_SELECTION")
            
            #If any result, append to validatie_lijnen
            validatie_lijnen = rf"{output}\validatie_lijnen"
            result_count = int(arcpy.management.GetCount(result)[0])
            if result_count > 0:
                arcpy.AddMessage(f"ValidatieA resultaten voor niveau {niveau} toevoegen aan output")
                arcpy.management.Append(result, validatie_lijnen, "NO_TEST")
            else:
                arcpy.AddMessage(f"Geen resultaten voor ValidatieA voor niveau {niveau}")

def validatieB(input, output):
    return
    
def validatieC(input, output):
    return

#Check and call the selected validations
if valicheckA == 1:
    arcpy.AddMessage("Start ValidatieA")
    validatieA(inputgdb, outputpath)
    arcpy.AddMessage("ValidatieA voltooid")
if valicheckB == 1:
    arcpy.AddMessage("Start ValidatieB")
    validatieB(inputgdb, outputpath)
    arcpy.AddMessage("ValidatieB voltooid")
if valicheckC == 1:
    arcpy.AddMessage("Start ValidatieC")
    validatieC(inputgdb, outputpath)
    arcpy.AddMessage("ValidatieC voltooid")

#Voeg output to aan ArcGIS
arcpy.AddMessage("Validatie output toevoegen aan ArcGIS Project")
arcpy.SetParameter(4, rf"{outputpath}\validatie_punten")
arcpy.SetParameter(5, rf"{outputpath}\validatie_lijnen")
arcpy.SetParameter(6, rf"{outputpath}\validatie_vlakken")

#Join VERSCHIL to validatieOUTPUT
#Stel een definition query in voor alle objecten die Verschil != Ongewijzigd
#Met bijv. lyr.updateDefinitionQueries