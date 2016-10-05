import functions

class Sideshot:
    """description of class"""

    def __init__(self,
                 instrument_point,
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
                 missing_value):
        
        self.instrument_point = functions.check_for_missing_value(instrument_point, missing_value)
        self.backsight_point = functions.check_for_missing_value(backsight_point, missing_value)
        self.foresight_point = functions.check_for_missing_value(foresight_point, missing_value)
        self.horizontal_angle = functions.check_for_missing_value(horizontal_angle, missing_value)
        self.horizontal_angle_standard_error = functions.check_for_missing_value(horizontal_angle_standard_error, missing_value)
        self.zenith_angle = functions.check_for_missing_value(zenith_angle, missing_value)
        self.zenith_angle_standard_error = functions.check_for_missing_value(zenith_angle_standard_error, missing_value)
        self.slope_distance = functions.check_for_missing_value(slope_distance, missing_value)
        self.slope_distance_error = functions.check_for_missing_value(slope_distance_standard_error, missing_value)
        self.prism_constant = functions.check_for_missing_value(prism_constant, missing_value)
        self.instrument_height = functions.check_for_missing_value(instrument_height, missing_value)
        self.target_height = functions.check_for_missing_value(target_height, missing_value)


