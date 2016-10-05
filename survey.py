import re
import os
import logging
import functions
import arcpy
import pyproj
from datetime import datetime
import point
import gps
from sideshot import Sideshot
import feature_class_definitions

template_spatial_reference = pyproj.Proj(init='epsg:6404')
lat_lon_spatial_ref = pyproj.Proj(init='epsg:4326')

class Survey:
    """description of class"""

    def __init__(self,
                 tdxf_file_path,
                 output_gdb_path,
                 output_primary_station_points_path,
                 output_secondary_station_points_path,
                 output_primary_traverse_polyline_path,
                 output_secondary_traverse_polyline_path,
                 output_tertiary_traverse_station_points_path,
                 output_tertiary_traverse_polyline_path):

        #validation
        self.tdxf_file_path = tdxf_file_path
        self.output_gdb_path = output_gdb_path
        self.output_primary_station_points_path = output_primary_station_points_path
        self.output_secondary_station_points_path = output_secondary_station_points_path
        self.output_primary_traverse_polyline_path = output_primary_traverse_polyline_path
        self.output_secondary_traverse_polyline_path = output_secondary_traverse_polyline_path
        self.output_tertiary_traverse_station_points_path = output_tertiary_traverse_station_points_path
        self.output_tertiary_traverse_polyline_path = output_tertiary_traverse_polyline_path

        self.process(tdxf_file_path)
        
    def initial_tdxf_file_read(self,
                               tdxf_file):
        with open(tdxf_file, 'r') as read_file:
            records_string = read_file.read()
        self.organized_records = organize_data_with_headers(records_string, '=')

    def process_general_records(self,
                                general_records):
        """
        processes a list of records contained in '[General]' section of Trimble file

        arguments:
        
            general_records -- list of 'General' records split by an equal sign,
            the result is each record is split into a record type (e.g. 'Source', 'ProjName', 'MissingValue', etc.) and the
            record information (e.g. 'Trimble Geomatics Office, Version 1.6', '20121226 River Primary (NAD832011ver2012)_Constrained', '?', etc. )

        There is only one type of 'General' record in a Trimble file:

            example:
         
                - 'ProjCoordinateZone=Arizona Central 0202'

        """

        survey_properties = {}
        for record in general_records:
            if len(record) > 1:
                survey_properties[record[0]] = record[1]
        return survey_properties

    def process_station_records(self,
                                stations_records,
                                records_separator,
                                missing_value):
        """
        processes a list of records contained in '[Stations]' section of Trimble file

        arguments:
        
            stations_records -- list of 'Stations' records split by an equal sign,
            the result is each record is split into a record type (e.g. 'Station') and the
            record information (e.g. '2:?:DESERT VIEW:36.040770869N:111.830256442W:2263.3631:559039.802:221146.274:2263.3631:1:1:0:AJ5640:AJ5640')

        There is only one type of 'Stations' record in a Trimble file:

            example:
         
                - 'Station=2:?:DESERT VIEW:36.040770869N:111.830256442W:2263.3631:559039.802:221146.274:2263.3631:1:1:0:AJ5640:AJ5640'

         """

        stations = {}
        for record in stations_records:
            record_type = record[0]
            record_information = get_record_information(record)
             
            if record_type == 'Station':
                if len(record_information.split(records_separator)) > 5:
                    station_name = record_information.split(records_separator)[2]
                    latitude = (determine_wgs_84_sign(functions.get_alpha_characters(record_information.split(records_separator)[3])) * \
                                functions.get_sign_digits_and_decimal(record_information.split(records_separator)[3]))
                    longitude = (determine_wgs_84_sign(functions.get_alpha_characters(record_information.split(records_separator)[4])) * \
                                    functions.get_sign_digits_and_decimal(record_information.split(records_separator)[4]))
                    elevation = functions.get_sign_digits_and_decimal(record_information.split(records_separator)[5])

                    #lambda x : float(x) if x != missing_value else None, record_information.split(records_separator)[6]
                    local_northing = functions.check_for_missing_value_float(record_information.split(records_separator)[6], missing_value)
                    local_easting = functions.check_for_missing_value_float(record_information.split(records_separator)[7], missing_value)
                    local_elevation = functions.check_for_missing_value_float(record_information.split(records_separator)[8], missing_value)

                    feature_code = record_information.split(records_separator)[-1]
                    station = point.Point(station_name,
                                          local_easting,
                                          local_northing,
                                          local_elevation,
                                          feature_code,
                                          longitude,
                                          latitude,
                                          elevation)
                    
                    #station.compare_local_coordinates_with_pyproj_transform_of_lat_lon(lat_lon_spatial_ref,
                    #                                                                   template_spatial_reference)

                    stations[station_name] = station
        return stations

    def process_keyed_in_coordinates_records(self,
                                             keyed_in_coordinate_records,
                                             stations,
                                             records_separator):
        """
        processes a list of records contained in '[Keyed In Coordinates]' section of Trimble file

        arguments:
        
            keyed_in_coordinate_records -- list of 'Keyed In Coordinates' records split by an equal sign,
            the result is each record is split into a record type (e.g. 'GridCoord' or 'LLCoord') and the
            record information (e.g. '1:?:DESERT VIEW:36.040770868N:111.830256442W:2263.363:?:C:C:U:E:W')

        There are two types of 'Keyed in Coordinate' records in a Trimble file:

            example one: GridCoord
         
             - 'GridCoord=1:?:CSC007437L:640995.033:237293.750:940.848:940.848:C:C:C:E'

            example two: LLCoord

             - 'LLCoord=1:?:DESERT VIEW:36.040770868N:111.830256442W:2263.363:?:C:C:U:E:W'
         
        """

        keyed_in_coordinates = {}
        
        for record in keyed_in_coordinate_records:
            record_type = record[0]
            record_information = get_record_information(record)

            if record_type == 'GridCoord':
                point_name = record_information.split(records_separator)[2]
                local_northing = functions.get_sign_digits_and_decimal(record_information.split(records_separator)[3])
                local_easting = functions.get_sign_digits_and_decimal(record_information.split(records_separator)[4])
                local_elevation = functions.get_sign_digits_and_decimal(record_information.split(records_separator)[5])
                feature_code = 'GridCoord'

                #todo: these values need to be retreived from the list of stations
                #longitude, latitude, elevation = pyproj.transform(template_spatial_reference,
                #                                                  lat_lon_spatial_ref,
                #                                                  local_easting,
                #                                                  local_northing,
                #                                                  local_elevation)

                if point_name in stations.keys():
                    latitude = stations[point_name].latitude
                    longitude = stations[point_name].longitude
                    elevation = stations[point_name].elevation

                    grid_coord = point.Point(point_name,
                                             local_easting,
                                             local_northing,                                         
                                             local_elevation,
                                             feature_code,
                                             longitude,
                                             latitude,
                                             elevation)

                    keyed_in_coordinates[point_name] = grid_coord

                else:
                    logging.warning('module:%s -- message: Point name: %s could not be found in stations' % (__name__, 
                                                                                                             self.point_name))
                    
            if record_type == 'LLCoord':
                point_name = record_information.split(records_separator)[2]
                latitude = (determine_wgs_84_sign(functions.get_alpha_characters(record_information.split(records_separator)[3])) * \
                            functions.get_sign_digits_and_decimal(record_information.split(records_separator)[3]))
                longitude = (determine_wgs_84_sign(functions.get_alpha_characters(record_information.split(records_separator)[4])) * \
                                functions.get_sign_digits_and_decimal(record_information.split(records_separator)[4]))
                elevation = functions.get_sign_digits_and_decimal(record_information.split(records_separator)[5])
                feature_code = 'LLCoord'
                
                #todo: these values need to be retreived from the list of stations
                #local_easting, local_northing, local_elevation = pyproj.transform(lat_lon_spatial_ref,
                #                                                                  template_spatial_reference,
                #                                                                  longitude,
                #                                                                  latitude,
                #                                                                  elevation)

                if point_name in stations.keys():
                    local_easting = stations[point_name].local_easting
                    local_northing = stations[point_name].local_northing
                    local_elevation = stations[point_name].local_elevation

                    ll_coord = point.Point(point_name,
                                            local_easting,
                                            local_northing,
                                            local_elevation,
                                            feature_code,
                                            longitude,
                                            latitude,                                        
                                            elevation)

                    keyed_in_coordinates[point_name] = ll_coord
                else:
                    logging.warning('module:%s -- message: Point name: %s could not be found in stations' % (__name__, 
                                                                                                             self.point_name))

        return keyed_in_coordinates

    def process_observed_coordinates_records(self,
                                             observed_coordinates_records):
        """
        processes a list of records contained in '[Observed Coordinates]' section of Trimble file

        arguments:
        
            observed_coordinates_records -- list of 'Observed Coordinates' records split by an equal sign,
            the result is each record is split into a record type (e.g. 'ObsCoord') and the
            record information (e.g. '1:?:FRAZ:35.783913561N:113.073117273W:1833.547:U:0:29 02 2004:22 56 32.0:02 03 2004:19 06 47.0:114:1.386:E')

        There is only one type of 'Observed Coordinates' record in a Trimble file:

            example:
         
             - 'ObsCoord=1:?:FRAZ:35.783913561N:113.073117273W:1833.547:U:0:29 02 2004:22 56 32.0:02 03 2004:19 06 47.0:114:1.386:E'

         """

        return

    def process_gps_records(self,
                            gps_records, 
                            records_separator,
                            missing_value):
        """

        """
        gps_observations = []
        for record in gps_records:
            record_type = record[0]
            record_information = get_record_information(record)
            
            if record_type == 'Vector':
                 from_station = record_information.split(records_separator)[2]            
                 to_station = record_information.split(records_separator)[3]
                 ecef_dx = record_information.split(records_separator)[4]
                 ecef_dy = record_information.split(records_separator)[5]
                 ecef_dz = record_information.split(records_separator)[6]
                 covariance_xx = record_information.split(records_separator)[7]
                 covariance_xy = record_information.split(records_separator)[8]
                 covariance_xz = record_information.split(records_separator)[9]
                 covariance_yy = record_information.split(records_separator)[10]
                 covariance_yz = record_information.split(records_separator)[11]
                 covariance_zz = record_information.split(records_separator)[12]
                 from_antenna_height = record_information.split(records_separator)[13]
                 to_antenna_height = record_information.split(records_separator)[14]
                 status = record_information.split(records_separator)[15]
                 ratio = record_information.split(records_separator)[16]
                 rms = record_information.split(records_separator)[17]
                 ref_var = record_information.split(records_separator)[18]
                 
                 start_datetime_string = ':'.join(record_information.split(records_separator)[19:21]) 
                 start_datetime = datetime.strptime(start_datetime_string[:-2], '%d %m %Y:%H %M %S') #index to [:-2] to get rid of trailing decimal of seconds
                 
                 end_datetime_string = ':'.join(record_information.split(records_separator)[21:23])
                 end_datetime = datetime.strptime(end_datetime_string[:-2], '%d %m %Y:%H %M %S')

                 observation = gps.Observation(from_station,            
                                               to_station,
                                               ecef_dx,
                                               ecef_dy,
                                               ecef_dz,
                                               covariance_xx,
                                               covariance_xy,
                                               covariance_xz,
                                               covariance_yy,
                                               covariance_yz,
                                               covariance_zz,
                                               from_antenna_height,
                                               to_antenna_height,
                                               status,
                                               ratio,
                                               rms,
                                               ref_var,
                                               start_datetime,
                                               end_datetime,
                                               missing_value)
                 gps_observations.append(observation)

        return gps_observations

    def process_terrestrial_records(self,
                                    terrestrial_records,
                                    records_separator,
                                    missing_value):
        """
        processes a list of records contained in '[Terrestrial]' section of Trimble file

        arguments:
        
            terrestrial_records -- list of 'Terrestrial' records split by an equal sign,
            the result is each record is split into a record type (e.g. 'TerrObs') and the
            record information (e.g. '1:?:LTC-000903R:LTC-001100L:LTC-001100L:0.000000000:0.001666667:89.205833333:0.002777778:324.568:8.2:?:1.650:1.750:?:?:2255:E')

        There is only one type of 'Terrestrial' record in a Trimble file:

            example:
         
             - 'TerrObs=1:?:LTC-000903R:LTC-001100L:LTC-001100L:0.000000000:0.001666667:89.205833333:0.002777778:324.568:8.2:?:1.650:1.750:?:?:2255:E'

         """

        terrestrial_observations = []
        for record in terrestrial_records:
            record_type = record[0]
            record_information = get_record_information(record)

            if record_type == 'TerrObs':
                instrument_point = record_information.split(records_separator)[2]
                backsight_point = record_information.split(records_separator)[3]
                foresight_point = record_information.split(records_separator)[4]
                horizontal_angle = record_information.split(records_separator)[5]
                horizontal_angle_standard_error = record_information.split(records_separator)[6]
                zenith_angle = record_information.split(records_separator)[7]
                zenith_angle_standard_error = record_information.split(records_separator)[8]
                slope_distance = record_information.split(records_separator)[9]
                slope_distance_standard_error = record_information.split(records_separator)[10]
                prism_constant = record_information.split(records_separator)[11]
                instrument_height = record_information.split(records_separator)[12]
                target_height = record_information.split(records_separator)[13]
                side_shot = Sideshot(instrument_point,
                                        backsight_point,
                                        foresight_point,
                                        horizontal_angle,
                                        horizontal_angle_standard_error,
                                        zenith_angle,
                                        zenith_angle_standard_error,
                                        slope_distance,
                                        slope_distance_standard_error,
                                        prism_constant,
                                        instrument_height,
                                        target_height,
                                        missing_value)

                terrestrial_observations.append(side_shot)

        return terrestrial_observations

    def process_laser_records(self):
        """
        currently not implemented
        """
        return

    def process_level_run_records(self):
        """
        currently not implemented
        """
        return

    def process_reduced_observations(self):
        """
        currently not implemented
        """
        return

    def process_azimuths_records(self):
        """
        currently not implemented
        """
        return

    def create_traverse_terrestrial_vector(self,
                                           stations,
                                           terrestrial_observations,
                                           output_gdb_path,
                                           output_vector_path):

        template_terrestrial_traverse = r'U:\scratch-workplace\control-network\data\wrk\control-network-template.gdb\terrestrial_traverse'
        feature_dataset_name = os.path.dirname(output_vector_path)
        polyline_name = os.path.basename(output_vector_path)

        arcpy.CreateFeatureclass_management(feature_dataset_name,
                                            polyline_name,
                                            'POLYLINE',
                                            has_z = 'ENABLED',
                                            template = template_terrestrial_traverse)
        print '%s created' % output_vector_path
        #feature_class_definitions.add_fields(output_terrestrial_traverse_polyline_path,
        #                                     feature_class_definitions.traverse_terrestrial_vector_field_definitions)
        
        with arcpy.da.InsertCursor(output_vector_path,
                                   ['SHAPE@',
                                    'NET_TAG',
                                    'NET_TYPE',
                                    'OBS_TYPE',
                                    'INSTRUMENT_PT',
                                    'BACKSIGHT_PT',
                                    'FORESIGHT_PT',
                                    'HORIZ_ANGLE',
                                    'HORIZ_ANGLE_STND_ERR',
                                    'ZENITH_ANGLE',
                                    'ZENITH_ANGLE_STND_ERR',
                                    'SLOPE_DIST',
                                    'SLOPE_DIST_STND_ERR',
                                    'PRISM_CONSTANT',
                                    'INSTRUMENT_HEIGHT',
                                    'TARGET_HEIGHT']) as in_cursor:

            for observation in terrestrial_observations:
                if observation.instrument_point in stations.keys() and \
                observation.backsight_point in stations.keys() and \
                observation.foresight_point in stations.keys():

                    start_point = stations[observation.instrument_point]
                    end_point = stations[observation.foresight_point]
                    start_point_gis = arcpy.Point(start_point.local_easting,
                                                  start_point.local_northing,
                                                  start_point.local_elevation)
                    
                    end_point_gis = arcpy.Point(end_point.local_easting,
                                                end_point.local_northing,
                                                end_point.local_elevation)
                    point_array = arcpy.Array()
                    point_array.add(start_point_gis)
                    point_array.add(end_point_gis)
                    traverse_vector = arcpy.Polyline(point_array,
                                                     template_spatial_reference)

                    net_tag = str(datetime.now().year)
                    net_type = 'Tertiary'
                    obs_type = 'Terrestrial'

                    traverse_vector.projectAs(arcpy.SpatialReference(6404))
                    in_cursor.insertRow([traverse_vector,
                                         net_tag,
                                         net_type,
                                         obs_type,
                                         observation.instrument_point,
                                         observation.backsight_point,
                                         observation.foresight_point,
                                         observation.horizontal_angle,
                                         observation.horizontal_angle_standard_error,
                                         observation.zenith_angle,
                                         observation.zenith_angle_standard_error,
                                         observation.slope_distance,
                                         observation.slope_distance_error,
                                         observation.prism_constant,
                                         observation.instrument_height,
                                         observation.target_height])
        return

    def create_traverse_gps_vector(self,
                                   stations,
                                   gps_observations,
                                   network_level_to_process,
                                   output_gdb_path,
                                   output_vector_path):

        template_gps_traverse = r'U:\scratch-workplace\control-network\data\wrk\control-network-template.gdb\gps_traverse'
        feature_dataset_name = os.path.dirname(output_vector_path)
        polyline_name = os.path.basename(output_vector_path)

        arcpy.CreateFeatureclass_management(feature_dataset_name,
											polyline_name,
											'POLYLINE',
											has_z = 'ENABLED',
                                            template = template_gps_traverse)
        print '%s created' % output_vector_path
        #feature_class_definitions.add_fields(output_gps_traverse_polyline_path,
        #                                     feature_class_definitions.traverse_gps_vector_field_definitions)

        with arcpy.da.InsertCursor(output_vector_path, ['SHAPE@',
                                                        'NET_TAG',
                                                        'NET_TYPE',
                                                        'OBS_TYPE',
                                                        'FROM_STATION',
                                                        'TO_STATION',
                                                        'ECEF_DX',
                                                        'ECEF_DY',
                                                        'ECEF_DZ',
                                                        'COVAR_XX' ,
                                                        'COVAR_XY',
                                                        'COVAR_XZ' ,
                                                        'COVAR_YY',
                                                        'COVAR_YZ',
                                                        'COVAR_ZZ',
                                                        'FROM_ANT_HT',
                                                        'TO_ANT_HT',
                                                        'PROCESS',
                                                        'RATIO',
                                                        'RMS',
                                                        'REF_VAR',
                                                        'START_TIME',
                                                        'END_TIME']) as in_cursor:
            for observation in gps_observations:
                if observation.from_station in stations.keys() and \
                observation.to_station in stations.keys():
                    if network_level != None:
                        if network_level.upper() == network_level_to_process.upper():

                            start_point = stations[observation.from_station]
                            end_point = stations[observation.to_station]
                            start_point_gis = arcpy.Point(start_point.local_easting,
                                                          start_point.local_northing,
                                                          start_point.local_elevation)
                    
                            end_point_gis = arcpy.Point(end_point.local_easting,
                                                        end_point.local_northing,
                                                        end_point.local_elevation)
                            point_array = arcpy.Array()
                            point_array.add(start_point_gis)
                            point_array.add(end_point_gis)
                            traverse_vector = arcpy.Polyline(point_array,
                                                             template_spatial_reference)

                            traverse_vector.projectAs(arcpy.SpatialReference(6404))
                            in_cursor.insertRow([traverse_vector, 
                                                 'NA',
                                                 network_level_to_process,
                                                 'GPS',
                                                 observation.from_station,
                                                 observation.to_station,
                                                 observation.ecef_dx,
                                                 observation.ecef_dy,
                                                 observation.ecef_dz,
                                                 observation.covariance_xx,
                                                 observation.covariance_xy,
                                                 observation.covariance_xz,
                                                 observation.covariance_yy,
                                                 observation.covariance_yz,
                                                 observation.covariance_zz,
                                                 observation.from_antenna_height,
                                                 observation.to_antenna_height,
                                                 observation.status,
                                                 observation.ratio,
                                                 observation.rms,
                                                 observation.ref_var,
                                                 observation.start_datetime,
                                                 observation.end_datetime])

        return

    def create_station_points_feature_class(self,
                                            stations,
                                            network_level_to_process,
                                            output_gdb_path,
                                            output_feature_class_path):

        template_control = r'U:\scratch-workplace\control-network\data\wrk\control-network-template.gdb\stations'
        feature_dataset_name = os.path.dirname(output_feature_class_path)
        point_feature_class_name = os.path.basename(output_feature_class_path)


        arcpy.CreateFeatureclass_management(feature_dataset_name,
                                            point_feature_class_name,
                                            'POINT',
                                            has_z = 'ENABLED',
                                            template = template_control)
            
        #feature_class_definitions.add_fields(output_feature_class_path,
        #                                     feature_class_definitions.station_field_definitions)
        print '%s created' % output_feature_class_path

        with arcpy.da.InsertCursor(output_feature_class_path, ['SHAPE@',
                                                              'POINT_NAME',
                                                              'LATITUDE',
                                                              'LONGITUDE',
                                                              'NORTHING',
                                                              'EASTING',
                                                              'ELLIPSE_Z',
                                                              'HEIGHT',
                                                              'MAJOR_AXIS',
                                                              'MINOR_AXIS',
                                                              'ORIENTATION',
                                                              'SIGMA_X',
                                                              'SIGMA_Y',
                                                              'SIGMA_H',
                                                              'CircularError_95Pct',
                                                              'Adjustment_Year',
                                                              'RiverMile', 
                                                              'Point_Code',
                                                              'Network',
                                                              'Point_Use',
                                                              'Monumentation']) as in_cursor:
            for key in stations.keys():
                
                network_level = point.get_control_network_level(key, feature_class_definitions.rim_stations)
                if network_level != None:
                    if network_level.upper() == network_level_to_process.upper():

                        pt = arcpy.Point(stations[key].local_easting, stations[key].local_northing, stations[key].local_elevation)
                        point_name = key
                        point_geometry = arcpy.PointGeometry(pt)
                        point_code = point_name[:3]
                
                        point_use = point.get_point_use(network_level, point_code)
                        monumentation = point.get_monumentation(network_level, point_code)
                
                        #todo:verify that I have correct values for ellipse_z and height
                        ellipse_z = stations[key].elevation
                        height = stations[key].local_elevation

                        #todo:get major_axis, minor_axis, orientation, sigma_x, sigma_y, sigma_h
                        major_axis, minor_axis, orientation, sigma_x, sigma_y, sigma_h = None, None, None, None, None, None

                        #todo:get circular_error_95pct
                        circular_error_95pct = None
                        if major_axis != None and minor_axis != None:
                            circular_error_95pct = major_axis / 2.445547 * (1.96079 + (0.004071 * minor_axis / major_axis)+ \
                                                  (0.114276 * minor_axis / major_axis) +(0.371625 * minor_axis / major_axis))

                        #todo:get adjustment year
                        adjustment_year = None

                        #todo:get river mile
                        river_mile = point.get_river_mile(point_name, feature_class_definitions.rim_stations)
                        print 'point name: %s : %s' % (point_name, river_mile)

                        in_cursor.insertRow([point_geometry,
                                            point_name,
                                            stations[key].latitude,
                                            stations[key].longitude,
                                            stations[key].local_easting,
                                            stations[key].local_northing,
                                            ellipse_z,
                                            height,
                                            major_axis,
                                            minor_axis,
                                            orientation,
                                            sigma_x,
                                            sigma_y,
                                            sigma_h,
                                            circular_error_95pct,
                                            adjustment_year,
                                            river_mile,                                    
                                            point_code,
                                            network_level,
                                            point_use,
                                            monumentation])

    def process(self,
                tdxf_file_path):
        
        self.initial_tdxf_file_read(tdxf_file_path)
        self.survey_properties = self.process_general_records(self.organized_records['General'])

        records_separator = ':'
        missing_value = '?'

        if 'Separator' in self.survey_properties.keys():
            records_separator = self.survey_properties['Separator']
        if 'MissingValue'  in self.survey_properties.keys():
            missing_value = self.survey_properties['MissingValue']

        self.control_points = []

        self.stations = self.process_station_records(self.organized_records['Stations'], 
                                                     records_separator,
                                                     missing_value)
        self.keyed_in_coordinates = self.process_keyed_in_coordinates_records(self.organized_records['Keyed In Coordinates'],
                                                                              self.stations,
                                                                              records_separator)
        self.observed_coordinates = self.process_observed_coordinates_records(self.organized_records['Observed Coordinates'])
        
        self.gps_observations = self.process_gps_records(self.organized_records['GPS'],
                                                         records_separator,
                                                         missing_value)
        #self.create_traverse_gps_vector(self.stations,
        #                                self.gps_observations,
        #                                'PRIMARY',
        #                                self.output_gdb_path,
        #                                self.output_primary_traverse_polyline_path)
        #self.create_traverse_gps_vector(self.stations,
        #                                self.gps_observations,
        #                                'SECONDARY',
        #                                self.output_gdb_path,
        #                                self.output_secondary_traverse_polyline_path)

        #todo: create way to account for RIM points
        self.create_station_points_feature_class(self.stations,
                                                 'PRIMARY',
                                                 self.output_gdb_path,
                                                 self.output_primary_station_points_path)

        self.create_station_points_feature_class(self.stations,
                                                 'SECONDARY',
                                                 self.output_gdb_path,
                                                 self.output_secondary_station_points_path)

        self.terrestrial_observations = self.process_terrestrial_records(self.organized_records['Terrestrial'],
                                                                         records_separator,
                                                                         missing_value)
        #self.create_traverse_terrestrial_vector(self.stations,
        #                                        self.terrestrial_observations,
        #                                        self.output_gdb_path,
        #                                        self.output_tertiary_traverse_polyline_path)

        self.create_station_points_feature_class(self.stations,
                                                 'TERTIARY',
                                                 self.output_gdb_path,
                                                 self.output_tertiary_traverse_station_points_path)

def get_general_survey_properties(records_string):
    survey_properties = {}
    general_survey_settings = records_string.split('\n\n')[0].split('\n')
    for setting in general_survey_settings:
        if len(setting.split('=')) == 2:
            survey_properties[setting.split('=')[0]] = setting.split('=')[1]
    return survey_properties

def get_organized_records(records_string,
                          separator):
    organized_records = [record.strip().split(separator) for record in records_string.splitlines()]
    return organized_records

def get_data_header_names(records_string):
    headers = re.findall(r'\[[a-zA-Z\s]+\]', records_string)
    return [header[1:-1] for header in headers]

def split_data_by_headers(records_string):
    return re.split(r'\[[a-zA-Z\s]+\]', records_string)

def organize_data_with_headers(records_string,
                               separator):
    headers_with_data = {}
    headers = get_data_header_names(records_string)
    records_divided_by_header = split_data_by_headers(records_string)
    for i in xrange(0, len(headers)):
        headers_with_data[headers[i]] = get_organized_records(records_divided_by_header[i+1], separator)
    return headers_with_data

def get_data_records(records_string,
                     separator):
    organized_records = [record.strip().split(separator) for record in re.split('\[[a-zA-Z\s]+\]', records_string)]
    return organized_records

def get_record_information(record):
    record_information = ''
    if len(record) >= 2:
        record_information = record[1]
    return record_information

def determine_wgs_84_sign(check_string):
    sign = 1
    if check_string != None:
        if check_string.upper() == 'S' or check_string.upper() == 'W':
            sign = -1
    return sign


