import re

def get_sign_digits_and_decimal(check_string):
    '''
        see here: http://stackoverflow.com/questions/385558/extract-float-double-value for r'[+-]? *(?:\d+(?:\.\d*)?|\.\d+)'
        and here: http://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string-in-python for r'[-+]?\d*\.\d+|\d+'
    '''
    floating_point_number_matches = re.findall(r'[+-]? *(?:\d+(?:\.\d*)?|\.\d+)',check_string)#[-+]?\d*\.\d+|\d+
    if len(floating_point_number_matches) == 1:
        return float(floating_point_number_matches[0])
    else:
        #print check_string
        return 0

def get_alpha_characters(check_string):
    alpha_character_matches = re.findall('[a-zA-Z]+', check_string)
    if len(alpha_character_matches) == 1:
        return str(alpha_character_matches[0])
    else:
        print check_string
        return None

def get_point_coordinate_by_name(point_name,
                                 point_dictionary):
    if point_name in point_dictionary.keys():
        return point_dictionary[point_name]
    else:
        return None

def check_for_missing_value(val, 
                            missing_value):
    return val if val != missing_value else None

def check_for_missing_value_float(val,
                                  missing_value):
    return float(val) if val != missing_value else None

