# trimble-control-network-processing

This program is designed to process trimble surveys of control networks.
It can be used to both update and create new point feature classes of the control points
and the polyline feature classes of the vectors used to collect each control point.

# Background

> GCMRC establishes and maintains accurate geographic control in the Grand Canyon that is essential for
accurate geo-referencing of remotely sensed data and spatial analysis of resource data using modern
image processing and GIS technologies.

> In order to meet GCMRC's positioning needs, the existing control network must be continually enhanced to 
provide the high accuracy required for use with the GPS and conventional measurements. In association
with the National Geodetic Survey (NGS), GCMRC has established a GPS control network of monumented
points having three dimensional positions.

> The established control on the rim transfers to river corridor control points through simultaneous GPS
occupations. Subsequently, positional accuracy from river corridor control points is transfered to all
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

### Coordinate Records

Coordinate Records all follow a similar syntax. The record type is contained in the first portion of the record
and is separated from the record info by an equal (=) sign. 

The record info portion of the record is separated by the value given for `Separator` contained in the `General`
section of the file. Generally the `Separator` is a colon (:)

#### Stations

  - example:
    - `Station=2:?:DESERT VIEW:36.040770869N:111.830256442W:2263.3631:559039.802:221146.274:2263.3631:1:1:0:AJ5640:AJ5640`

#### Keyed In Coordinates

##### Grid Coord

  - example:
    - `GridCoord=1:?:CSC007437L:640995.033:237293.750:940.848:940.848:C:C:C:E`

##### LLCoord

  - example:
    - `LLCoord=1:?:DESERT VIEW:36.040770868N:111.830256442W:2263.363:?:C:C:U:E:W`
	
#### GPS

  - example:
    - `Vector=1:?:ABYSS:DAVIAN:-67332.6186:44737.5911:19991.5340:0.00000020:0.00000044:-0.00000033:0.00000113:-0.00000084:0.00000069:0.000:2.000:Postprocessed:13.4:0.010:0.820:15 09 2005:23 19 32.0:16 09 2005:19 51 32.0:E:Static or fast static:Static or fast static:Fixed:Iono Free`
  
#### Terrestrial

  - example:
    - `TerrObs=1:?:LTC-000903R:LTC-001100L:LTC-001100L:0.000000000:0.001666667:89.205833333:0.002777778:324.568:8.2:?:1.650:1.750:?:?:2255:E`

	
Need to find actual specifications of the file.
	

