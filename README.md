# trimble-control-network-processing

This program is designed to process trimble surveys of control networks.
It can be used to both update and create new point feature classes of the control points
and the polyline feature classes of the vectors used to collect each control point.

# Background



# Inputs

 - .asc trimble TDXF file
 
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
 
These tasks still need to get done.


