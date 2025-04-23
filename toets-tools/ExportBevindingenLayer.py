output_txt_file = r"G:\civ\IGA_ATG\Organisatie\Projecten\CW\TestBende\bevindingen.txt"
with open(output_txt_file, "w", encoding="utf-8") as file:
    file.write("Nummer\tOmschrijving\n")
    with arcpy.da.SearchCursor("Bevindingen", ["Nummer", "Omschrijving"]) as cursor:
        for row in cursor:
            nummer = row[0] if row[0] is not None else ""
            omschrijving = row[1] if row[1] is not None else ""
            file.write(f"{nummer}\t{omschrijving}\n")