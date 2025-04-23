fc = arcpy.management.CreateFeatureclass(
    out_path="in_memory",
    out_name="Bevindingen",
    geometry_type="POINT",
    spatial_reference=arcpy.SpatialReference(28992))
arcpy.management.AddField(fc, "Nummer", "TEXT")
arcpy.management.AddField(fc, "Omschrijving", "TEXT")


