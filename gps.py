import functions


class Observation:
    """description of class"""

    def __init__(self,
                 from_station,
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
                 missing_value):

        self.from_station = functions.check_for_missing_value(from_station, missing_value)
        self.to_station = functions.check_for_missing_value(to_station, missing_value)
        self.ecef_dx = functions.check_for_missing_value(ecef_dx, missing_value)
        self.ecef_dy = functions.check_for_missing_value(ecef_dy, missing_value)
        self.ecef_dz = functions.check_for_missing_value(ecef_dz, missing_value)
        self.covariance_xx = functions.check_for_missing_value(covariance_xx, missing_value)
        self.covariance_xy = functions.check_for_missing_value(covariance_xy, missing_value)
        self.covariance_xz = functions.check_for_missing_value(covariance_xz, missing_value)
        self.covariance_yy = functions.check_for_missing_value(covariance_yy, missing_value)
        self.covariance_yz = functions.check_for_missing_value(covariance_yz, missing_value)
        self.covariance_zz = functions.check_for_missing_value(covariance_zz, missing_value)
        self.from_antenna_height = functions.check_for_missing_value(from_antenna_height, missing_value)
        self.to_antenna_height = functions.check_for_missing_value(to_antenna_height, missing_value)
        self.status = functions.check_for_missing_value(status, missing_value)
        self.ratio = functions.check_for_missing_value(ratio, missing_value)
        self.rms = functions.check_for_missing_value(rms, missing_value)
        self.ref_var  = functions.check_for_missing_value(ref_var, missing_value)
        self.start_datetime = functions.check_for_missing_value(start_datetime, missing_value)
        self.end_datetime = functions.check_for_missing_value(end_datetime, missing_value)








