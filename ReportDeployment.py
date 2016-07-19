#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import os
import urllib
import shutil
import sys
import xml.etree.ElementTree as ET

#sys.tracebacklimit=0

#-----------------------------------------------------------------------------------------#
#--------------------------Environment Variable Parameters -------------------------------#
#-----------------------------------------------------------------------------------------#

print 'Checking Environment Variables ...'
error = 0

env_jasper_url = os.environ.get('JASPER_URL')
env_jasper_username = os.environ.get('JASPER_USER')
env_jasper_password = os.environ.get('JASPER_PASSWORD')
env_connectionUrl = os.environ.get('REDSHIFT_URL')
env_connectionDatabase = os.environ.get('REDSHIFT_DATABASE')
env_connectionUser = os.environ.get('REDSHIFT_USER')
env_connectionPassword = os.environ.get('REDSHIFT_PASSWORD')
env_repository_path = os.environ.get('PROJECT_NAME')

if not env_jasper_url : error = 1; print '---> JASPER_URL is missing'
if not env_jasper_username : error = 1; print '---> JASPER_USER is missing'
if not env_jasper_password : error = 1; print '---> JASPER_PASSWORD is missing'
if not env_connectionUrl : error = 1; print '---> REDSHIFT_URL is missing'
if not env_connectionUser : error = 1; print '---> REDSHIFT_USER is missing'
if not env_connectionPassword : error = 1; print '---> REDSHIFT_PASSWORD is missing'
if not env_repository_path : error = 1; print '---> PROJECT_NAME is missing'

if error != 0 :  print '\n\n**** Deployment Terminated ****' , sys.exit(1)
else : print '\n- Ok -'

#-----------------------------------------------------------------------------------------#
#-------------------------------- Jasper Parameters --------------------------------------#
#-----------------------------------------------------------------------------------------#

current_path = os.path.dirname(os.path.abspath(__file__))
files_path = os.path.abspath(current_path+'/../..')
base_files_path = os.path.abspath(current_path+'/..')

repository_path= '/' + str(env_repository_path)
redshift_connectionURL = str(env_connectionUrl) + '/' + str(env_connectionDatabase)
jasper_url = env_jasper_url
jasper_username = urllib.quote(env_jasper_username, safe='')
jasper_password = urllib.quote(env_jasper_password, safe='')

#-----------------------------------------------------------------------------------------#
#------------------------- Reading Manifest and Config files -----------------------------#
#-----------------------------------------------------------------------------------------#

with open('config.json') as config_file:    
    config = json.load(config_file)

manifest_path = os.environ.get('MANIFEST_PATH') if os.environ.has_key('MANIFEST_PATH') else files_path+config['git']['repository_path']+'/manifest.json'
with open(manifest_path) as manifest_file:    
    manifest = json.load(manifest_file)

#-----------------------------------------------------------------------------------------#
#----------------------------------- Parameters ------------------------------------------#
#-----------------------------------------------------------------------------------------#

#Git repository Information
datasource_path = files_path+config['git']['repository_path']+'/'+config['git']['datasource_folder_name']

report_path = files_path+config['git']['repository_path']+'/'+config['git']['report_folder_name']
base_report_path = base_files_path+config['git']['repository_path']+'/'+config['git']['report_folder_name']

input_control_path = files_path+config['git']['repository_path']+'/'+config['git']['input_controls_folder_name']
base_input_control_path = base_files_path+config['git']['repository_path']+'/'+config['git']['input_controls_folder_name']

query_path = files_path+config['git']['repository_path']+'/'+config['git']['query_folder_name']
base_query_path = base_files_path+config['git']['repository_path']+'/'+config['git']['query_folder_name']

query_file_list = []
inputControl_file_list = []
reports_file_list = []

#-----------------------------------------------------------------------------------------#
#----------------------------- Checking Datasource ---------------------------------------#
#-----------------------------------------------------------------------------------------#

print "\nChecking the availability of DataSource .."

if not os.path.isfile(datasource_path+'/'+manifest['jasper']['datasource']+'.xml'):
    raise Exception("No Such Datasource : "+manifest['jasper']['datasource'])

print "\n- Ok -"

#-----------------------------------------------------------------------------------------#
#------------------------------- Checking Reports ----------------------------------------#
#-----------------------------------------------------------------------------------------#

print "\nChecking the availability of Report files .."
report_count = len(manifest['jasper']['reports'])

for i in range(0,report_count):
    if not os.path.isfile(report_path+'/'+manifest['jasper']['reports'][i]+'_files/main_jrxml.data'):
    	if not os.path.isfile(base_report_path+'/'+manifest['jasper']['reports'][i]+'_files/main_jrxml.data'):
            raise Exception("No Such Report : "+manifest['jasper']['reports'][i])
        else : reports_file_list.append(base_report_path+'/'+manifest['jasper']['reports'][i])
    else:reports_file_list.append(report_path+'/'+manifest['jasper']['reports'][i])#+'_files/main_jrxml.data'

print "\n- Ok -"
#-----------------------------------------------------------------------------------------#
#--------------------------- Checking Input Controls -------------------------------------#
#-----------------------------------------------------------------------------------------#

print "\nChecking the availability of Input Controls of Reports ..\n"
inputControl_error = 0
input_error_array = []

for i in reports_file_list:
    reporttree = ET.parse(i+'.xml')
    for j in range(0,len(reporttree.findall('./inputControl/uri'))):
        inputcontrol_name = os.path.basename(reporttree.findall('./inputControl/uri')[j].text)
        if not os.path.exists(input_control_path +'/'+inputcontrol_name+'.xml'):
            if not os.path.exists(base_input_control_path +'/'+inputcontrol_name+'.xml'):
                inputControl_error = 1
                if inputcontrol_name not in input_error_array:
                    print '---> Input Control '+inputcontrol_name+' Missing'
                    input_error_array.append(inputcontrol_name)
            else: 
                if base_input_control_path +'/'+inputcontrol_name+'.xml' not in inputControl_file_list:
                    inputControl_file_list.append(base_input_control_path +'/'+inputcontrol_name+'.xml')
        else: 
            if input_control_path +'/'+inputcontrol_name+'.xml' not in inputControl_file_list:
                inputControl_file_list.append(input_control_path +'/'+inputcontrol_name+'.xml')
            

if inputControl_error != 0 : print '\n\n**** Deployment Terminated ****' , sys.exit(1)
else : print '- Ok -'

#-----------------------------------------------------------------------------------------#
#------------------------------ Checking Queries -----------------------------------------#
#-----------------------------------------------------------------------------------------#

print "\nChecking the availability of Queries of InputControls ..\n"
query_error = 0l
query_error_array = []

for i in inputControl_file_list:
    reporttree = ET.parse(i)
    for j in range(0, len(reporttree.findall('./query/uri'))):
        query_name = os.path.basename(reporttree.findall('./query/uri')[j].text)
        if not os.path.exists(query_path + '/' + query_name + '.xml'):
            if not os.path.exists(base_query_path + '/' + query_name + '.xml'):
                query_error = 1
                if query_name not in query_error_array:
                    print '---> Query ' + query_name + ' Missing'
                    query_error_array.append(query_name)
            else:
                if base_query_path + '/' + query_name + '.xml' not in query_file_list:
                    query_file_list.append(base_query_path + '/' + query_name + '.xml')
        else:
            if query_path + '/' + query_name + '.xml' not in query_file_list:
                query_file_list.append(query_path + '/' + query_name + '.xml')

if query_error != 0:print '''**** Deployment Terminated ****''', sys.exit(1)
else:print '- Ok -'

            

#-----------------------------------------------------------------------------------------#
#--------------------- Deletes the Project Folder If Exists ------------------------------#
#-----------------------------------------------------------------------------------------#

project_folder = jasper_url+'/rest/resource'+repository_path
del_response = requests.get(url=project_folder, auth=(jasper_username,jasper_password))
if not del_response.status_code == 404:
  requests.delete(url=project_folder, auth=(jasper_username,jasper_password))
  print("\nDeleted existing "+os.path.basename(repository_path)+" folder")
  

#-----------------------------------------------------------------------------------------#
#----------------------- Creating Jasper Project Folders ---------------------------------#
#-----------------------------------------------------------------------------------------#

sys.path.insert(0, current_path + '/helper_modules')
import create_folder as folder

folder.create_folder(jasper_url,jasper_username,jasper_password,repository_path)
print "\n"+os.path.basename(repository_path) + " Created"
folders = ["DataSource","Report","InputControl","Query"]
print '\nCreating Folders...\n'
for folder_name in folders:
        folder.create_folder(jasper_url,jasper_username,jasper_password,repository_path+'/'+folder_name)
        print folder_name
print '\nDone !!'


#-----------------------------------------------------------------------------------------#
#-------------------------------- Jasper Deployment --------------------------------------#
#-----------------------------------------------------------------------------------------#
import report_upload as ru
import datasource_upload as dsu
import inputcontrol_upload as icu
import query_upload as qu

#-------------------------------- Uploading DataSource -----------------------------------#

print '\nDeploying DataSource...'
file_path = datasource_path+'/'+manifest['jasper']['datasource']+'.xml'
datasource_deploy_path = repository_path + '/DataSource/' + manifest['jasper']['datasource']
dbName = dsu.report_upload(datasource_deploy_path,file_path,jasper_url,jasper_username,jasper_password,redshift_connectionURL,env_connectionUser,env_connectionPassword)
print "\n- "+ dbName
print "\nDone !!"

#Jasper Repository paths
jasper_inputControl_path = repository_path + '/InputControl/'
jasper_query_path = repository_path + '/Query/'
jasper_datasource_path = repository_path + '/DataSource'+'/'+ dbName

#-------------------------------- Uploading Queries --------------------------------------#

if len(query_file_list) != 0 :
	print '\nDeploying Queries...\n'
	for index,path in query_file_list:
		query_deploy_path = jasper_query_path + os.path.splitext(os.path.basename(path))[0]
		qu.report_upload(query_deploy_path,path,jasper_url,jasper_username,jasper_password,jasper_datasource_path)
		print '- '+os.path.splitext(os.path.basename(path))[0]
	print "\nDone !!"
#------------------------------ Uploading InputControls ----------------------------------#

if len(inputControl_file_list) != 0 :
	print '\nDeploying Input Controls...\n'
	for path in inputControl_file_list:
		inputControl_deploy_path = jasper_inputControl_path + os.path.splitext(os.path.basename(path))[0]
		icu.report_upload(inputControl_deploy_path,path,jasper_url,jasper_username,jasper_password,jasper_datasource_path,jasper_query_path)
		print '- '+os.path.splitext(os.path.basename(path))[0]
	print "\nDone !!"

#--------------------------------- Uploading Reports -------------------------------------#

def xml_update(input_control_path,root,tree):
         resourceDescriptor = ET.Element('resourceDescriptor')
         resourceDescriptor.attrib['isNew']='false'
         resourceDescriptor.attrib['wsType']='inputControl'
         root.append(resourceDescriptor)
         name = ['PROP_REFERENCE_URI','PROP_IS_REFERENCE']
         values = [input_control_path,'true']
         for i in range(0,len(name)):
          resourceProperty=ET.Element('resourceProperty')
          resourceProperty.attrib['name']=name[i]
          resourceDescriptor.append(resourceProperty)
         
          value=ET.Element('value')
          resourceProperty.append(value)
          value.append(ET.Comment(' --><![CDATA[' + (values[i]).replace(']]>', ']]]]><![CDATA[>') + ']]><!-- '))

         tree.write(report_resc_desc_path_temp)

def subreport_xml_update(name,path,root,tree):
    resourceDescriptor = ET.Element('resourceDescriptor')
    resourceDescriptor.attrib['name']=name
    resourceDescriptor.attrib['wsType']='jrxml'
    resourceDescriptor.attrib['uriString']=path+'/'+name
    resourceDescriptor.attrib['isNew']='false'    
    
    root.append(resourceDescriptor)
    label = ET.Element('label')
    resourceDescriptor.append(label)
    label.append(ET.Comment(' --><![CDATA[' + (name).replace(']]>', ']]]]><![CDATA[>') + ']]><!-- '))
    
    property_list = ['PROP_RESOURCE_TYPE','PROP_PARENT_FOLDER','PROP_IS_REFERENCE','PROP_HAS_DATA','PROP_ATTACHMENT_ID']
    property_values = ['com.jaspersoft.jasperserver.api.metadata.common.domain.FileResource',path,'false','true','attachment']
    for i in range(0,len(property_list)):
        resourceProperty=ET.Element('resourceProperty')
        resourceProperty.attrib['name']=property_list[i]
        resourceDescriptor.append(resourceProperty)

        value=ET.Element('value')
        resourceProperty.append(value)
        value.append(ET.Comment(' --><![CDATA[' + (property_values[i]).replace(']]>', ']]]]><![CDATA[>') + ']]><!-- '))
        
    tree.write(report_resc_desc_path_temp)

subreport_list = []
if len(inputControl_file_list) != 0 :
    report_resc_desc_path = current_path+'/helper_modules/templates/report_res_descr.xml'
    report_resc_desc_path_temp = current_path+'/helper_modules/templates/report_res_descr_temp.xml'
    print '\nDeploying Reports...\n'
    for i in reports_file_list:
      file_path = i+'_files/main_jrxml.data'
      report_deploy_path = repository_path + '/Report/' + os.path.basename(i)
      reporttree = ET.parse(i+'.xml')
      report_label = reporttree.findall('./label')[0].text
      #creating the temp file for dynamic resource descriptor
      desc_tree = ET.parse(report_resc_desc_path)
      desc_tree.write(report_resc_desc_path_temp) #In case of No input Controls in Reports
      desc_root = desc_tree.getroot()
      for j in range(0,len(reporttree.findall('./inputControl/uri'))):
        inputcontrol_name = os.path.basename(reporttree.findall('./inputControl/uri')[j].text)
        xml_update(repository_path + '/InputControl/' +inputcontrol_name,desc_root,desc_tree)
        
      for j in range(0,len(reporttree.findall('./resource'))):
                     subreport_name = os.path.basename(reporttree.findall('./resource/localResource/name')[j].text)
                     subreport_path = repository_path + '/Report/' +os.path.basename(reporttree.findall('./resource/localResource/folder')[j].text)
                     subreport_xml_update(subreport_name,subreport_path,desc_root,desc_tree)
                     subreport_list.append(i + '_files/' + subreport_name)
                     
      datasource_filepath = repository_path + '/DataSource/' + dbName
      ru.report_upload(report_deploy_path,file_path,datasource_filepath,jasper_url,jasper_username,jasper_password,report_label,subreport_list)
      os.remove(report_resc_desc_path_temp)
      print "- " + os.path.basename(i)

    print '\nDone !!'

print "\n--Deployment Completed--"   
#-----------------------------------------------------------------------------------------#
#-------------------------------- End of Deployment --------------------------------------#
#-----------------------------------------------------------------------------------------#
