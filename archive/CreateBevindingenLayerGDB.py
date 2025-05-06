import arcpy

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
cnummer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Text, Required
outputgdb = arcpy.GetParameterAsText(1) #Configure paramterer: Input, Folder, 
outputlayer = arcpy.GetParameterAsText(2) #Configure parameter: Output, Feature Layer, Derived

#Doorloop elke DTB layer in the output.gdb
def createEmptyLayer(cnummer, outputgdb):
    
    #Create New Layer
    layername = rf"Bevindingen_{cnummer}"
    gdb = arcpy.management.CreateFileGDB(outputgdb, layername, "10.0")
    layer = arcpy.management.CreateFeatureclass(
        out_path=gdb,
        out_name=layername,
        geometry_type="POINT",
        spatial_reference=arcpy.SpatialReference(28992))
    
    #Set Fields
    arcpy.management.AddField(layer, "Type", "TEXT")
    arcpy.management.AddField(layer, "Omschrijving", "TEXT")
    
    #Set domain for 'Type'
    arcpy.management.CreateDomain(gdb, "fouten_domein", domain_type="CODED", field_type="TEXT")
    domeinkeuzes = {
        "Huppeldepup":"Fout op Huppeldepup",
        "Dinges":"Fout in Dinges",
        "Enzovoort":"Fout in Enzovoort"}
    for fouttype in domeinkeuzes:        
        arcpy.management.AddCodedValueToDomain(gdb, "fouten_domein", fouttype, domeinkeuzes[fouttype])
    arcpy.management.AssignDomainToField(layer, "Type", "fouten_domein")    
    
    #Enable attachments for screenshots
    arcpy.management.EnableAttachments(layer)
    
    #Add layer with symbology based on derived output parameter 'outputlayer'
    arcpy.SetParameter(2, layer)
    
createEmptyLayer(cnummer, outputgdb)