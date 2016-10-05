import arcpy
import os

traverse_terrestrial_vector_field_definitions = {'NET_TAG' : ('TEXT', 0),
                                              'NET_TYPE' : ('TEXT', 0),
                                              'OBS_TYPE' : ('TEXT', 0),
                                              'INSTRUMENT_PT' : ('TEXT', 0),
                                              'BACKSIGHT_PT' : ('TEXT', 1),
                                              'FORESIGHT_PT' : ('TEXT', 2),
                                              'HORIZ_ANGLE' : ('DOUBLE', 3),
                                              'HORIZ_ANGLE_STND_ERR' : ('DOUBLE',4),
                                              'ZENITH_ANGLE' : ('DOUBLE', 5),
                                              'ZENITH_ANGLE_STND_ERR' : ('DOUBLE', 6),
                                              'SLOPE_DIST' : ('DOUBLE', 7),
                                              'SLOPE_DIST_STND_ERR' : ('DOUBLE', 8),
                                              'PRISM_CONSTANT' : ('DOUBLE', 9),
                                              'INSTRUMENT_HEIGHT' : ('DOUBLE', 10),
                                              'TARGET_HEIGHT' : ('DOUBLE', 11)}

traverse_gps_vector_field_definitions = {'NET_TAG' : ('TEXT', 0),
                                        'NET_TYPE' : ('TEXT', 0),
                                        'OBS_TYPE' : ('TEXT', 0),
                                        'FROM_STATION' : ('TEXT', 0),
                                        'TO_STATION' : ('TEXT', 0),
                                        'ECEF_DX' : ('DOUBLE', 0),
                                        'ECEF_DY' : ('DOUBLE', 0),
                                        'ECEF_DZ' : ('DOUBLE', 0),
                                        'COVAR_XX' : ('DOUBLE', 0),
                                        'COVAR_XY' : ('DOUBLE', 0),
                                        'COVAR_XZ' : ('DOUBLE', 0),
                                        'COVAR_YY' : ('DOUBLE', 0),
                                        'COVAR_YZ' : ('DOUBLE', 0),
                                        'COVAR_ZZ' :('DOUBLE', 0),
                                        'FROM_ANT_HT' : ('DOUBLE', 0),
                                        'TO_ANT_HT' : ('DOUBLE', 0),
                                        'PROCESS' : ('TEXT', 0),
                                        'RATIO' : ('DOUBLE', 0),
                                        'RMS' : ('DOUBLE', 0),
                                        'REF_VAR' : ('DOUBLE', 0),
                                        'START_TIME' : ('DATE', 0),
                                        'END_TIME' : ('DATE', 0)}

station_field_definitions = {'POINT_NAME' : ('TEXT', 0),
                           'LATITUDE' : ('DOUBLE', 1),
                           'LONGITUDE' : ('DOUBLE', 2),
                           'NORTHING': ('DOUBLE', 3),
                           'EASTING' : ('DOUBLE', 4),
                           'ELLIPSE_Z' : ('DOUBLE', 5),
                           'HEIGHT' : ('DOUBLE', 0),
                           'MAJOR_AXIS' : ('DOUBLE', 0),
                           'MINOR_AXIS' : ('DOUBLE', 0),
                           'ORIENTATION' : ('TEXT', 0),
                           'SIGMA_X' : ('DOUBLE', 0),
                           'SIGMA_Y' : ('DOUBLE', 0),
                           'SIGMA_H' : ('DOUBLE', 0),
                           'CircularError_95Pct' : ('DOUBLE', 0),
                           'Adjustment_Year' : ('SHORT', 0),
                           'RiverMile' : ('DOUBLE', 0), 
                           'Point_Code' : ('TEXT', 5),
                           'Network' : ('TEXT', 6),
                           'Point_Use' : ('TEXT', 7),
                           'Monumentation' : ('TEXT', 8)}

sorted_traverse_terrestrial_vector_field_definitions = sorted(traverse_terrestrial_vector_field_definitions.items(), key = lambda x:x[1][1])


rim_stations = ['6652 CANYON',
                'ABYSS',
                'AIRPORT',
                'AIRPORT RM 1',
                'AIRPORT RM 2',
                'BADGER',
                'CAVE',
                'DAVIAN',
                'DESERT VIEW',
                'ECHO',
                'EMIN',
                'EMIN REF 1',
                'FRAZ',
                'JACK',
                'L 404',
                'LFRG',
                'MARBLE CANYON',
                'NAVAJO POINT',
                'Q 389',
                'R 389',
                'REDWALL',
                'SALT CANYON',
                'SB POINT',
                'SHIVWITS',
                'SIGNAL HILL',
                'SOUTH CANYON TRA'
                'T 96',
                'TENDERFOOT',
                'WHITMORE',
                'APEX']


def add_fields(output_feature_class,
               field_definitions_dictionary):
    in_gdb = check_if_in_geodatabase(output_feature_class)
    for field in field_definitions_dictionary.keys():
        field_name = field
        if in_gdb == False:
            field_name = field[:10]
        arcpy.AddField_management(output_feature_class, 
                                  field_name, 
                                  field_definitions_dictionary[field][0])
        print 'Added field %s to %s' % (field_name, os.path.basename(output_feature_class))

def check_if_in_geodatabase(gis_data_path):
    in_gdb = False
    if arcpy.Exists(gis_data_path):
        folder_path = os.path.dirname(gis_data_path)
        gdb_string = os.path.split(folder_path)
        if gdb_string != None:
            if len(gdb_string) > 1:
                if len(gdb_string[-1].split('.')) == 2:
                    if gdb_string[-1].split('.')[-1] == 'gdb':
                        in_gdb = True
    return in_gdb

