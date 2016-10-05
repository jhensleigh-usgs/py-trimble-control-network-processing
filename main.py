import os
import arcpy
from Survey import Survey
import feature_class_definition

tdxf_file = r'U:\scratch-workplace\control-network\data\raw\2016_0216_TDXF_GCD-BAC.asc'

template_shapefile_path = r'U:\scratch-workplace\control-network\scripts\wrk\template_control_network.shp'
#template_spatial_reference = arcpy.Describe(template_shapefile_path).spatialReference
#print template_spatial_reference.name, template_spatial_reference.factoryCode
#lat_lon_spatial_ref = arcpy.SpatialReference(4326)

#possible_transformations = arcpy.ListTransformations(lat_lon_spatial_ref, template_spatial_reference)

output_folder = r'U:\scratch-workplace\control-network\data\wrk'
output_gdb_name = r'control-network.gdb'
output_gdb_path = os.path.join(output_folder, output_gdb_name)

if arcpy.Exists(output_gdb_path):
    arcpy.Delete_management(output_gdb_path)

arcpy.CreateFileGDB_management(output_folder, output_gdb_name)


output_fc_name = 'traverse_2016_0216_TDXF_GCD_BAC'
output_fc_path = os.path.join(output_gdb_path, output_fc_name)
if arcpy.Exists(output_fc_path):
    arcpy.Delete_management(output_fc_path)

if arcpy.Exists(output_gdb_path):
    arcpy.CreateFeatureclass_management(output_gdb_path,
                                        output_fc_name,
                                        'POLYLINE',
                                        has_z = 'ENABLED')

    feature_class_definition.add_tdxf_polyline_fields(output_fc_path, 
                                                      feature_class_definition.field_definitions)

tdxf_survey = Survey(tdxf_file,
                     output_fc_path)