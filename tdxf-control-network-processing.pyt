import os
import sys
import logging
import arcpy
import feature_class_definitions
from survey import Survey

logging.basicConfig(filename=r'U:\scratch-workplace\control-network\data\wrk\processing.log', filemode = 'w', level=logging.DEBUG)

spatial_reference_template = r'U:\scratch-workplace\control-network\data\wrk\control-network-template.gdb\terrestrial_traverse'


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Traverse_Network_Processing, Control_Point_Network_Processing]


class Traverse_Network_Processing(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Traverse Network Processing"
        self.description = "Draws vectors between control network points."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName = 'Input TDXF File',
								 name = 'tdxf_file_path',
								 datatype = 'DEFile',
								 parameterType = 'Required',
								 direction = 'Input')
        if param0.altered:
            tdxf_file_path = param0.valueAsText
            if tdxf_file_path != None:
                if os.path.exists(tdxf_file_path) == False:
                    param0.setErrorMessage('The file provided does not exist.')
        
        param1 = arcpy.Parameter(displayName = 'Output Folder',
				 name = 'output_folder',
				 datatype = 'DEFolder',
				 parameterType = 'Required',
				 direction = 'Input')
        
        if param1.altered:
            output_folder = param1.valueAsText
            if output_folder != None:
                if os.path.exists(output_folder) == False:
                    param1.setErrorMessage('The folder provided does not exist.')

        param2 = arcpy.Parameter(displayName = 'Output Geodatabase Name',
				 name = 'output_gdb_name',
				 datatype = 'String',
				 parameterType = 'Required',
				 direction = 'Input')
        param2.value = 'control-network.gdb'

        param3 = arcpy.Parameter(displayName = 'Output Feature Class Name',
								 name = 'output_fc_name',
								 datatype = 'String',
								 parameterType ='Required',
								 direction = 'Input')
        param3.value = 'traverse'

        if param1.valueAsText != None and param2.valueAsText != None and param3.valueAsText != None:
            output_fc_path = os.path.join(param1.valueAsText, param2.valueAsText, param3.valueAsText)
            if arcpy.Exists(output_fc_path) == True:
                param3.setErrorMessage('The provided feature class name already exists in the output file geodatabase.')

        param4 = arcpy.Parameter(displayName = 'Export CSV',
                                 name = 'export_as_csv',
                                 datatype = 'GPBoolean',
                                 parameterType = 'Optional',
                                 direction = 'Input')

        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        try:

            ##actual tool
            #tdxf_file_path = parameters[0].valueAsText
            #output_folder = parameters[1].valueAsText
            #output_gdb_name = parameters[2].valueAsText
            #output_fc_polyline_name = parameters[3].valueAsText
            #output_fc_point_name = 'control'
        
            ##test parameters
            ##https://blogs.esri.com/esri/arcgis/2012/12/14/how-to-debug-python-toolboxes-in-3-easy-steps/
            tdxf_file_path = r'U:\scratch-workplace\control-network\data\raw\2016_0216_TDXF_GCD-BAC.asc'#NA2011_primary TDXF.asc
        
            #file gdb
            output_folder = r'U:\scratch-workplace\control-network\data\wrk'
            output_gdb_name = r'control-network.gdb'
            output_gdb_path = os.path.join(output_folder, output_gdb_name)

            #feature datasets
            output_primary_secondary_network_name = 'Primary_Secondary_Networks'
            output_primary_secondary_network_path = os.path.join(output_gdb_path, output_primary_secondary_network_name)
            output_tertiary_network_name = 'Tertiary_Networks'
            output_tertiary_network_path  = os.path.join(output_gdb_path, output_tertiary_network_name)

            #feature class names - primary and secondary
            output_primary_traverse_polyline_name = 'primary_traverse'
            output_secondary_traverse_polyline_name = 'secondary_traverse'
            output_primary_station_points_name = 'Primary_Stations'
            output_secondary_station_points_name = 'Secondary_Stations'

            #feature class names - tertiary network
            output_tertiary_traverse_polyline_name = 'Traverse'
            output_tertiary_traverse_station_points_name = 'Traverse_Stations'
             
                                       
            if arcpy.Exists(output_gdb_path) == True:
                raise Exception('Path provided to file geodatabase already exists. Please choose another path.')
            else:
                arcpy.CreateFileGDB_management(output_folder, output_gdb_name)

                #create feature datasets
                arcpy.CreateFeatureDataset_management(output_gdb_path, output_primary_secondary_network_name, spatial_reference_template)
                arcpy.CreateFeatureDataset_management(output_gdb_path, output_tertiary_network_name, spatial_reference_template)

                #create paths to primary secondary network feature classes
                output_primary_traverse_polyline_path = os.path.join(output_primary_secondary_network_path, output_primary_traverse_polyline_name)
                output_secondary_traverse_polyline_path = os.path.join(output_primary_secondary_network_path, output_secondary_traverse_polyline_name)
                output_primary_station_points_path = os.path.join(output_primary_secondary_network_path, output_primary_station_points_name)
                output_secondary_station_points_path = os.path.join(output_primary_secondary_network_path, output_secondary_station_points_name)
                
                #create paths to tertiary network feature classes
                output_tertiary_traverse_polyline_path = os.path.join(output_tertiary_network_path, output_tertiary_traverse_polyline_name)
                output_tertiary_traverse_station_points_path = os.path.join(output_tertiary_network_path, output_tertiary_traverse_station_points_name)    

                tdxf_survey = Survey(tdxf_file_path,
                                     output_gdb_path,
                                     output_primary_station_points_path,
                                     output_secondary_station_points_path,
                                     output_primary_traverse_polyline_path,
                                     output_secondary_traverse_polyline_path,
                                     output_tertiary_traverse_station_points_path,
                                     output_tertiary_traverse_polyline_path)
        
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print '%s\nType: %s\nLine: %s' % (exc_value, exc_type, exc_traceback.tb_lineno)
            logging.critical('module:%s --  message: %s Type: %s Line: %s' % (__name__, exc_value, exc_type, exc_traceback.tb_lineno))

        return

class Control_Point_Network_Processing(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Control Point Network Processing"
        self.description = "produces control point network from tdxf file."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName = 'Input TDXF File',
								 name = 'tdxf_file_path',
								 datatype = 'DEFile',
								 parameterType = 'Required',
								 direction = 'Input')
        if param0.altered:
            tdxf_file_path = param0.valueAsText
            if tdxf_file_path != None:
                if os.path.exists(tdxf_file_path) == False:
                    param0.setErrorMessage('The file provided does not exist.')
        
        param1 = arcpy.Parameter(displayName = 'Output Folder',
				 name = 'output_folder',
				 datatype = 'DEFolder',
				 parameterType = 'Required',
				 direction = 'Input')
        
        if param1.altered:
            output_folder = param1.valueAsText
            if output_folder != None:
                if os.path.exists(output_folder) == False:
                    param1.setErrorMessage('The folder provided does not exist.')

        param2 = arcpy.Parameter(displayName = 'Output Geodatabase Name',
				 name = 'output_gdb_name',
				 datatype = 'String',
				 parameterType = 'Required',
				 direction = 'Input')
        param2.value = 'control-network.gdb'

        param3 = arcpy.Parameter(displayName = 'Output Feature Class Name',
								 name = 'output_fc_name',
								 datatype = 'String',
								 parameterType ='Required',
								 direction = 'Input')
        param3.value = 'points'

        if param1.valueAsText != None and param2.valueAsText != None and param3.valueAsText != None:
            output_fc_path = os.path.join(param1.valueAsText, param2.valueAsText, param3.valueAsText)
            if arcpy.Exists(output_fc_path) == True:
                param3.setErrorMessage('The provided feature class name already exists in the output file geodatabase.')

        param4 = arcpy.Parameter(displayName = 'Export CSV',
                                 name = 'export_as_csv',
                                 datatype = 'GPBoolean',
                                 parameterType = 'Optional',
                                 direction = 'Input')

        params = [param0, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        ##actual tool
        tdxf_file_path = parameters[0].valueAsText
        output_folder = parameters[1].valueAsText
        output_gdb_name = parameters[2].valueAsText
        output_fc_name = parameters[3].valueAsText
        
        ##test parameters
        ##https://blogs.esri.com/esri/arcgis/2012/12/14/how-to-debug-python-toolboxes-in-3-easy-steps/
        #tdxf_file_path = r'U:\scratch-workplace\control-network\data\raw\2016_0216_TDXF_GCD-BAC.asc'#NA2011_primary TDXF.asc'
        #output_folder = r'U:\scratch-workplace\control-network\data\wrk'
        #output_gdb_name = r'control-network.gdb'
        #output_fc_name = 'traverse'
        output_gdb_path = os.path.join(output_folder, output_gdb_name)

        if arcpy.Exists(output_gdb_path) == False:
            #arcpy.Delete_management(output_gdb_path)
            arcpy.CreateFileGDB_management(output_folder, output_gdb_name)
        
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
            


        tdxf_survey = Survey(tdxf_file_path,
                             output_fc_path)
        
        return

def main():
    tbx = Toolbox()
    tool = Traverse_Network_Processing()
    tool.execute(tool.getParameterInfo(), None)

if __name__ == '__main__':
    main()

