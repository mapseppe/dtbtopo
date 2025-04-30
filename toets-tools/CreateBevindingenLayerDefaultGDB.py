import arcpy

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
cnummer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Text, Required
outputlayer = arcpy.GetParameterAsText(1) #Configure parameter: Output, Feature Layer, Derived

#Doorloop elke DTB layer in the output.gdb
def createEmptyLayer(cnummer):
    arcproj = arcpy.mp.ArcGISProject("CURRENT")
    gdb = arcproj.defaultGeodatabase
    layername = rf"Bevindingen_{cnummer}"
    layer = arcpy.management.CreateFeatureclass(
        out_path=gdb,
        out_name=layername,
        geometry_type="POINT",
        spatial_reference=arcpy.SpatialReference(28992))

    arcpy.management.AddField(layer, "Volgnummer", "TEXT")
    arcpy.management.AddField(layer, "Fout", "TEXT")
    arcpy.management.AddField(layer, "Omschrijving", "TEXT")
    arcpy.management.AddField(layer, "Bijlage_nr", "TEXT")
 
    domains = arcpy.da.ListDomains(gdb)
    domain_names = [d.name for d in domains]
    arcpy.AddMessage(domain_names)
    if "fouten_domein" not in domain_names:
        arcpy.management.CreateDomain(gdb, "fouten_domein", domain_type="CODED", field_type="TEXT")
        domeinkeuzes = {
            "Hier wordt niet voldaan aan de eisen gesteld aan de bestandsopbouw":"Hier wordt niet voldaan aan de eisen gesteld aan de bestandsopbouw",
            "Hier wordt niet voldaan aan de eisen gesteld aan de attribuutwaarden":"Hier wordt niet voldaan aan de eisen gesteld aan de attribuutwaarden",
            "Hier wordt niet voldaan aan de eisen gesteld aan de inwinning van objecten":"Hier wordt niet voldaan aan de eisen gesteld aan de inwinning van objecten",
            "Hier sluit het nieuwe DTB niet goed aan op het oude DTB":"Hier sluit het nieuwe DTB niet goed aan op het oude DTB",
            "Hier wordt niet voldaan aan de eisen gesteld aan de volledigheid":"Hier wordt niet voldaan aan de eisen gesteld aan de volledigheid",
            "Hier wordt niet voldaan aan de eisen gesteld aan de meetpunten":"Hier wordt niet voldaan aan de eisen gesteld aan de meetpunten"
            }
        for fouttype in domeinkeuzes:        
            arcpy.management.AddCodedValueToDomain(gdb, "fouten_domein", fouttype, domeinkeuzes[fouttype])

    arcpy.management.AssignDomainToField(layer, "Fout", "fouten_domein")    
    arcpy.SetParameter(1, layer)
    
createEmptyLayer(cnummer)