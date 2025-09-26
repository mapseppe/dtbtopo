import arcpy
from random import uniform

#interpreter C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3

arcpy.env.overwriteOutput = True

#Default ArcPro en Geodatabase constants
arcproj = arcpy.mp.ArcGISProject("CURRENT")
gdb = arcproj.defaultGeodatabase

def checkCurrentDomains():
    #Check of het domein al bestaat en zo niet maak het aan
    arcpy.AddMessage("Check of domein al bestaat")
    domains = arcpy.da.ListDomains(gdb)
    domain_names = [d.name for d in domains]
    
    if "fouten_domein" in domain_names:
        deleteDomain("fouten_domein")
        createDomain()
    else:
        createDomain()
        
    if "zichtbaar_domein" in domain_names:
        deleteDomain("zichtbaar_domein")
        createZichtbaarDomain()
    else:
        createZichtbaarDomain()
        
    if "voorkomen_domein" in domain_names:
        deleteDomain("voorkomen_domein")
        createVoorkomenDomain()
    else:
        createVoorkomenDomain()
        
def createDomain():
    arcpy.AddMessage("Nieuw domein aanmaken")
    arcpy.management.CreateDomain(gdb, "fouten_domein", domain_type="CODED", field_type="TEXT")
    domain_path = r"G:\civ\IGA_ATG\Producten\BGT\Toetstooling\dropdown-menu\invulvelden.txt"
    arcpy.AddMessage("Domeinpad openen")
    with open(domain_path, 'r') as domainfile:
        arcpy.AddMessage("Regels lezen")
        lines = [line.strip() for line in domainfile if line.strip()]
    arcpy.AddMessage("Regels converteren naar library")
    domeinkeuzes = {line: line for line in lines}
    arcpy.AddMessage("Domeinkeuzes toevoegen aan domein")
    for fouttype in domeinkeuzes:        
        arcpy.management.AddCodedValueToDomain(gdb, "fouten_domein", fouttype, domeinkeuzes[fouttype])
    
def createZichtbaarDomain():
    arcpy.management.CreateDomain(gdb, "zichtbaar_domein", domain_type="CODED", field_type="TEXT")
    arcpy.management.AddCodedValueToDomain(gdb, "zichtbaar_domein", "Ja", "Ja")
    arcpy.management.AddCodedValueToDomain(gdb, "zichtbaar_domein", "Nee", "Nee")

def createVoorkomenDomain():
    arcpy.management.CreateDomain(gdb, "voorkomen_domein", domain_type="CODED", field_type="TEXT")
    arcpy.management.AddCodedValueToDomain(gdb, "voorkomen_domein", "Eenmalig", "Eenmalig")
    arcpy.management.AddCodedValueToDomain(gdb, "voorkomen_domein", "Meermalig", "Meermalig")

def deleteDomain(domainname):
    arcpy.AddMessage("Oud domein re-namen")
    randomnr = uniform(100000, 999999)
    domeinrename = f"{domainname}{randomnr}"
    arcpy.management.AlterDomain(gdb, domainname, domeinrename)

checkCurrentDomains()