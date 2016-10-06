# trimble-control-network-processing

This program is designed to process trimble surveys of control networks.
It can be used to both update and create new point feature classes of the control points
and the polyline feature classes of the vectors used to collect each control point.

# Background

GCMRC establishes and maintains accurate geographic control in the Grand Canyon that is essential for
accurate geo-referencing of remotely sensed data and spatial analysis of resource data using modern
image processing and GIS technologies.

In order to meet GCMRC's positioning needs, the existing control network must be continually enhanced to 
provide the high accuracy required for use with the GPS and conventional measurements. In association
with the National Geodetic Survey (NGS), GCMRC has established a GPS control network of monumented
points having three dimensional positions.

The established control on the rim transfers to river corridor control points through simultaneous GPS
occupatoins. Subsequently, positional accuracy from river corridor control points is transfered to all
mapping along the river corridor through conventional 
techniques ([Brown, K.M., Gonzales, M., & Kohl, K. 2003](http://www.gcmrc.gov/library/posters_delme/Q12003/controlposter.pdf)).


# Inputs

 - .asc trimble TDXF or TDEF file
 
# Outputs
  - file geodatabase (gdb) containing: 
    - Feature datasets: 
      - Primary Secondary Networks which contains 4 feature classes:
        - Point feature classes:	 
	      - Primary_Stations
	      - Secondary_Stations	   
	- Polyline feature classes:	   
      - Primary Vectors
      - Secondary Vectors	   
    - Tertiary Networks:
	  - Point feature classes:
	    - Traverse_Stations	  
	- Polyline feature classes:	 
	 - Traverse_Vectors 

# TODO:
  - [ ] Parse out Tertiary network into established river mile sections
  - [ ] Hard points?
  - [ ] Replace access database with Oracle database

# Technical Info

## Trimble TDXF/TDEF .asc File

TDXF/TDEF files are made up of 10 unique headers:
  
  - General
    - contains general info about the survey, such as projection used, pressure units, and missing values symbol within the file
  - Stations
    - coordinate info (both lat/long and projected Northing/Easting) and other information associated with stations
  -	Keyed In Coordinates
    - coordinate info for two different types of points:
	  - GridCoord
	    - coordinate stored in projected coordinates
	  - LLCoord
	    - coordinate stored in lat/long
  - Observed Coordinates
    - Unknown
  - GPS
    - coordinate pairs that create a vector from one point to another
  - Terrestrial
    - raw trigonometry values to calculate a point from instrument point, backsight point, and foresight point
  - Laser
    - Unknown
  - Level Run
    - Unknown
  - Reduced Observations
    - Unknown
  - Azimuths
    - Unknown

Need to find actual specifications of the file.
	

