import arcpy
import arcpy.management

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

#Environment
arcpy.env.overwriteOutput = True

#Parameter
ivrinummer = arcpy.GetParameterAsText(0) #Configure parameter: Input, Text, Required
outputlayer = arcpy.GetParameterAsText(1) #Configure parameter: Output, Feature Layer, Derived

#Paths for change comparison
arcpy.AddMessage("Setting paths")
basepath = rf"M:\IVRI\{ivrinummer}"
uitsnedegdb = rf"{basepath}\export\output.gdb\DTB_DATA"
verschilgdb = rf"{basepath}\Verschil\verschil.gdb\DTB_DATA"

#Define vlakkennet layers en domeinen
arcpy.AddMessage("Defining layers")
vlakkennetlayers = ["DTB_BEBOUWING_VLAKKEN", "DTB_BEKLEDING_VLAKKEN", "DTB_GROND_VLAKKEN", "DTB_INSTALLATIE_VLAKKEN", "DTB_TERREIN_VLAKKEN", "DTB_VERHARDING_VLAKKEN", "DTB_WATER_VLAKKEN"]
vlaknetdomeinen = ["dDTB_TYPE_BVK", "dDTB_TYPE_BKV", "dDTB_TYPE_GVK", "dDTB_TYPE_IVK", "dDTB_TYPE_TVK", "dDTB_TYPE_VVK", "dDTB_TYPE_WVK"]
uitsnedelayers = [rf"{uitsnedegdb}\{layer}" for layer in vlakkennetlayers]
verschillayers = [rf"{verschilgdb}\{layer}" for layer in vlakkennetlayers]

#Merge en union vlakkennet layers
arcpy.AddMessage("Merging layers")
uitsnedemerge = arcpy.management.Merge(uitsnedelayers, rf"in_memory\uitsnede")
verschilmerge = arcpy.management.Merge(verschillayers, rf"in_memory\verschil")

#Verschil layer maken
for niveau in [0, 1, 2, 3]:
    arcpy.AddMessage(rf"Calculating difference for niveau: {niveau}")
    niveauselection = rf'"NIVEAU" = {niveau}'
    uitsnedemerge = arcpy.management.SelectLayerByAttribute(uitsnedemerge, "NEW_SELECTION", niveauselection)
    verschilmerge = arcpy.management.SelectLayerByAttribute(verschilmerge, "NEW_SELECTION", niveauselection)
    selection_count = int(arcpy.management.GetCount(uitsnedemerge)[0])
    if selection_count > 0:
        arcpy.AddMessage("Creating union")
        if niveau == 0:
            vlaknetunion = arcpy.analysis.Union([uitsnedemerge, verschilmerge], rf"{verschilgdb}\DTB_VLAKKENNET_VERSCHIL")
        else:
            vlaknetunion = arcpy.analysis.Union([uitsnedemerge, verschilmerge], rf"in_memory\union{niveau}")
            arcpy.management.Append(vlaknetunion, rf"{verschilgdb}\DTB_VLAKKENNET_VERSCHIL", "NO_TEST")

#Aan project toevoegen
arcpy.AddMessage("Filtering Union")
result = rf"{verschilgdb}\DTB_VLAKKENNET_VERSCHIL"
resultlayer = arcpy.management.MakeFeatureLayer(result, "Gewijzigd Vlakkennet (2D)")
arcpy.SetParameter(1, resultlayer)

#Filteren
filterexpression = "TYPE = TYPE_1 OR TYPE = 0 OR TYPE_1 = 0"
arcpy.management.SelectLayerByAttribute(resultlayer, "NEW_SELECTION", filterexpression)
arcpy.management.DeleteRows(resultlayer)

#Verander fieldnames
arcpy.AddMessage("Altering field names")
arcpy.management.AlterField(resultlayer, "TYPE_1", "TYPE_nieuw", "TYPE_nieuw")
arcpy.management.AlterField(resultlayer, "DTB_ID_1", "DTB_ID_nieuw", "DTB_ID_nieuw")

#Domein toevoegen
arcpy.AddMessage("Importing domain")
geodatabase = rf"{basepath}\Verschil\verschil.gdb"
domaintable = rf"G:\civ\IGA_ATG\Producten\DTB\Toetstooling\dropdown-menu\domein_vlakkennet.csv"
arcpy.management.TableToDomain(domaintable, "Code", "Description", geodatabase, "resultDomain", "", "REPLACE")

arcpy.AddMessage("Applying domain to fields")
arcpy.management.AssignDomainToField(resultlayer, "TYPE", "resultDomain")
arcpy.management.AssignDomainToField(resultlayer, "TYPE_nieuw", "resultDomain")

#Hieronder hoeft enkel bij datamodel wijzigen gedraaid te worden en de domeinlijst te vervangern
# geodatabase = rf"M:\IVRI\archive\124\Verschil\verschil.gdb"
# vlaknetdomeinen = ["dDTB_TYPE_BVK", "dDTB_TYPE_BKV", "dDTB_TYPE_GVK", "dDTB_TYPE_IVK", "dDTB_TYPE_TVK", "dDTB_TYPE_VVK", "dDTB_TYPE_WVK"]
# all_domains = arcpy.da.ListDomains(geodatabase)
# vlaknetdomains = [dom for dom in all_domains if dom.name in vlaknetdomeinen]

# combined_coded_values = {}
# for domain in vlaknetdomains:
#     for code, desc in domain.codedValues.items():
#         combined_coded_values.setdefault(code, desc)
# print(combined_coded_values)