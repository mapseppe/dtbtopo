import arcpy

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
ivrinummer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Text, Required
outputlayer = arcpy.GetParameterAsText(1) #Configure parameter: Output, Feature Layer, Derived

#Default ArcPro en Geodatabase constants
arcproj = arcpy.mp.ArcGISProject("CURRENT")
gdb = arcproj.defaultGeodatabase

#Doorloop elke DTB layer in the output.gdb
def createEmptyLayer(ivrinummer):
    #Nieuwe layer voor huidige ArcPro sessie
    arcpy.AddMessage("Nieuwe laag creëren")
    layername = rf"Bevindingen_{ivrinummer}"
    layer = arcpy.management.CreateFeatureclass(
        out_path=gdb,
        out_name=layername,
        template=r"G:\civ\IGA_ATG\Producten\DTB\Toetstooling\datamodel_template\datamodel_template.shp",
        geometry_type="POINT",
        spatial_reference=arcpy.SpatialReference(28992))
    
    #Voeg velden toe aan laag
    #arcpy.AddMessage("Velden toevoegen aan laag")
    #arcpy.management.AddField(layer, "Volgnummer", "TEXT")
    #arcpy.management.AddField(layer, "Zichtbaar", "TEXT")
    #arcpy.management.AddField(layer, "Fout", "TEXT")
    #arcpy.management.AddField(layer, "Omschrijving", "TEXT", field_length=2000)
    #arcpy.management.AddField(layer, "Bijlage_nr", "TEXT")
    #arcpy.management.AddField(layer, "xcoord", "LONG")
    #arcpy.management.AddField(layer, "ycoord", "LONG")
    arcpy.management.AssignDefaultToField(layer, "Zichtbaar", "Ja")
 
    #Check of het domein al bestaat en zo niet maak het aan
    arcpy.AddMessage("Check of domein al bestaat")
    domains = arcpy.da.ListDomains(gdb)
    domain_names = [d.name for d in domains]
    if "fouten_domein" not in domain_names or "zichtbaar_domein" not in domain_names:
        arcpy.AddError("Geen domeinen gevonden, draai eerst tool 0. Update Drop-downmenu om deze toe te voegen") 
    else:
        arcpy.AddMessage("Domein toevoegen aan nieuwe layer veld")
        arcpy.management.AssignDomainToField(layer, "Fout", "fouten_domein")
        arcpy.management.AssignDomainToField(layer, "Zichtbaar", "zichtbaar_domein")
    
        #Apply standaard symbologie voor layer
        arcpy.AddMessage("Laag toevoegen aan project")
        arcpy.SetParameter(1, layer)

createEmptyLayer(ivrinummer)