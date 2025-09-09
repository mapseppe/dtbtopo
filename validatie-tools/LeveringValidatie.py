import arcpy
import os

#Parameters for inputs and outputs
ivrinummer = arcpy.GetParameterAsText(0) #Input, String
validatieA = arcpy.GetParameterAsText(1) #Input, Boolean
validatieB = arcpy.GetParameterAsText(2) #Input, Boolean
validatieC = arcpy.GetParameterAsText(3) #Input, Boolean
output_punt = arcpy.GetParameterAsText(4) #Output, Derived, Feature Layer, Symbology instellen
output_lijn = arcpy.GetParameterAsText(5) #Output, Derived, Feature Layer, Symbology instellen
output_vlak = arcpy.GetParameterAsText(6) #Output, Derived, Feature Layer, Symbology instellen

#Script with main functionality that is initially activated
def main_script():
    
    #Check if IVRI-nummer exists
    ivripath = rf"M:\IVRI\{ivrinummer}"
    if os.path.exists(ivripath) and os.path.isdir(ivripath):
        arcpy.AddMessage(f"Start validatie voor {ivrinummer}")
    else:
        arcpy.AddError(f"IVRI nummer bestaat niet op de M-Schijf: {ivripath}")

    #Determine the paths of the input and output.gdb .gdb
    inputgdb = rf"M:\IVRI\{ivrinummer}\Verschil\verschil.gdb"
    outputgdb_template = rf"G:\civ\IGA_ATG\Producten\DTB\Toetstooling - AAT Next\template_output\template_output.gdb"
    outputpath = rf"M:\IVRI\{ivrinummer}\validatie_output.gdb"

    #Create an empty output.gdb to which validation results will be written
    arcpy.AddMessage("validatie.gdb aanmaken")
    arcpy.management.Copy(outputgdb_template, outputpath)

    #Check and call the selected validations
    if validatieA == "true":
        try:
            arcpy.AddMessage("Start ValidatieA")
            validatieA(inputgdb, outputpath)
            arcpy.AddMessage("ValidatieA voltooid")
        except:
            arcpy.AddMessage("ValidatieA error")

    if validatieB == "true":
        try:
            arcpy.AddMessage("Start ValidatieB")
            validatieB(inputgdb, outputpath)
            arcpy.AddMessage("ValidatieB voltooid")
        except:
            arcpy.AddMessage("ValidatieB error")
    
    if validatieC == "true":
        try:
            arcpy.AddMessage("Start ValidatieC")
            validatieC(inputgdb, outputpath)
            arcpy.AddMessage("ValidatieC voltooid")
        except:
            arcpy.AddMessage("ValidatieC error")

    #Voeg output to aan ArcGIS
    arcpy.AddMessage("Validatie output toevoegen aan ArcGIS Project")
    arcpy.SetParameter(4, rf"{outputpath}\validatie_punten")
    arcpy.SetParameter(5, rf"{outputpath}\validatie_lijnen")
    arcpy.SetParameter(6, rf"{outputpath}\validatie_vlakken")

    #Stel een definition query in voor alle objecten die Verschil != Ongewijzigd
    #Met bijv. lyr.updateDefinitionQueries
    #Stel symbology in

def validatieA(input, output):
    return

def validatieB(input, output):
    return
    
def validatieC(input, output):
    return

main_script()