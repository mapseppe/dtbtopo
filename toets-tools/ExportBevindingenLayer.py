import arcpy

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
inputlayer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Feature Layer, Required
outputtxtfile = arcpy.GetParameterAsText(1) #Configure parameter: Input, 

output_txt_file = outputtxtfile
with open(output_txt_file, "w", encoding="utf-8") as file:
    file.write("Type\tOmschrijving\n")
    with arcpy.da.SearchCursor(inputlayer, ["Type", "Omschrijving"]) as cursor:
        for row in cursor:
            type = row[0] if row[0] is not None else ""
            omschrijving = row[1] if row[1] is not None else ""
            file.write(f"{type}\t{omschrijving}\n")