import pyproj
import functions
import logging

class Point:
    """description of class"""

    def __init__(self,
                 point_name,
                 local_easting,
                 local_northing,
                 local_elevation,
                 feature_code,
                 longitude = None,
                 latitude = None,
                 elevation = None):
        
        self.point_name = point_name
        self.local_easting = local_easting
        self.local_northing = local_northing
        self.local_elevation = local_elevation
        self.feature_code = feature_code
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation

    def print_summary(self):
        print 'Name: %s (X: %s, Y: %s, Z: %s) Code: %s' % (self.point_name,
                                                           self.local_easting,
                                                           self.local_northing,
                                                           self.local_elevation,
                                                           self.feature_code)
    def compare_local_coordinates_with_pyproj_transform_of_lat_lon(self,
                                                                   lat_lon_spatial_ref,
                                                                   projected_spatial_ref):
        
        if self.longitude != None and self.latitude != None and self.elevation != None and self.local_elevation != None: 
            x2, y2, z2 = pyproj.transform(lat_lon_spatial_ref,
                                          projected_spatial_ref,
                                          self.longitude,
                                          self.latitude,
                                          self.elevation)
                    
            #test projection calculation
            difference_easting = self.local_easting - x2
            difference_northing = self.local_northing - y2
            difference_elevation = self.local_elevation - z2
            print '(delta northing: %s, delta easting: %s, delta elevation: %s' % (difference_northing, difference_easting, difference_elevation)
            if round(difference_easting, 3) != 0 or \
            round(difference_northing, 3) != 0 or \
            round(difference_elevation, 3) != 0:
                logging.warning('module:%s -- message: Point name: %s has issues with coordinate differences (%s, %s, %s)' % (__name__, 
                                                                                                                              self.point_name, 
                                                                                                                              difference_easting,
                                                                                                                              difference_northing,
                                                                                                                              difference_elevation))
        else:
            logging.warning('module:%s -- message: Point name: %s missing values for lat(%s), lon(%s), and/or elevation(%s)' % (__name__, 
                                                                                                                                self.point_name,
                                                                                                                                self.latitude,
                                                                                                                                self.longitude,
                                                                                                                                self.elevation))
            print 'longitude, latitude, and elevation must be set to compare elevations.'

def get_control_network_level(point_name, rim_stations = []):
    control_level = None
    if point_name != None:
        if len(point_name) >= 2:
            #print 'check-string: %s' % check_string
            control_level_character = point_name[1]
            #print '%s : %s' % (control_level_character, check_string[1])
            if control_level_character.upper() == 'P' or point_name in rim_stations:
                control_level = 'Primary'
            elif control_level_character.upper() == 'S':
                control_level = 'Secondary'
            elif control_level_character.upper() == 'T':
                control_level = 'Tertiary'
    return control_level

def get_river_mile(point_name, exclude_points = []):
    river_mile = None
    if point_name not in exclude_points:
        river_mile_info = point_name[3:]
        river_side = river_mile_info[-1]
        river_mile = functions.get_sign_digits_and_decimal(point_name)
        if river_mile != 0:
            river_mile = round((river_mile/1000), 3)
        else:
            print 'Invalid river mile (%s) for point name: %s' % (river_mile, point_name)
            logging.warning('module:%s -- message: Invalid river mile (%s) for point name: %s' % (__name__, river_mile, point_name))
            #raise Exception('Invalid river mile (%s) for point name: %s' % (river_mile, point_name))
    return river_mile

def get_point_use(control_level,
                  point_code):
    point_use = None
    if control_level != None and point_code != None:
        if point_code in point_use_and_monument_lookup[control_level.upper()].keys():
            point_use = point_use_and_monument_lookup[control_level.upper()][point_code]['point_use']
        else:
            point_use = 'Control'
    return point_use

def get_monumentation(control_level,
                      point_code):
    monumentation = None
    if control_level != None and point_code != None:
        if point_code in point_use_and_monument_lookup[control_level.upper()].keys():
            monumentation = point_use_and_monument_lookup[control_level.upper()][point_code]['monumentation']
    return monumentation

point_use_and_monument_lookup  = {'TERTIARY' : {'CTH' : {'point_use' : 'Horizontal Check',
                                                'monumentation' : 'NOT MONUMENTED'},
                                               'CTV' : {'point_use' :'Vertical Check',
                                                        'monumentation' : 'NOT MONUMENTED'},
                                               'CTP' : {'point_use' : 'Panel Check',
                                                        'monumentation' : 'NOT MONUMENTED'},
                                               'CTB' : {'point_use' : 'Bathymetry',
                                                        'monumentation' : 'INK X'},
                                               'CTG' : {'point_use' : 'USGS Gage Cap',
                                                        'monumentation' : None },
                                               'CTN' : {'point_use' : 'Navigation',
                                                        'monumentation' : 'UNRECORDED'},
                                               'CTS' : {'point_use' : 'Side Shot',
                                                        'monumentation' : 'See Monument Table'},
                                               'CTT' : {'point_use' : 'Instrument Station',
                                                        'monumentation' : 'INK X'},
                                               'CTW' : {'point_use' : 'Water Surface Mark',
                                                        'monumentation' : None},
                                               'CTX' : {'point_use' : 'Cross Section',
                                                        'monumentation' : 'BOLT'},
                                               'CSO' : {'point_use' : 'Observation',
                                                        'monumentation' : 'See Monument Table'}},
                         'SECONDARY' : {},
                         'PRIMARY' : {}}
