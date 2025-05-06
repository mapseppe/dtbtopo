import arcpy

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
cnummer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Text, Required
outputlayer = arcpy.GetParameterAsText(1) #Configure parameter: Output, Feature Layer, Derived

#Doorloop elke DTB layer in the output.gdb
def createEmptyLayer(cnummer):
    layername = rf"Bevindingen_{cnummer}"
    layer = arcpy.management.CreateFeatureclass(
        out_path="in_memory",
        out_name=layername,
        geometry_type="POINT",
        spatial_reference=arcpy.SpatialReference(28992))

    arcpy.management.AddField(layer, "Type", "TEXT")
    arcpy.management.AddField(layer, "Omschrijving", "TEXT")

    arcpy.SetParameter(1, layer)
    
createEmptyLayer(cnummer)