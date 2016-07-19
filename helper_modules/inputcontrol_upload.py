import requests
import logging
import argparse
import httplib 
import jinja2
import os
import xml.etree.ElementTree as ET


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def render_template(template, **params):
  """Return rendered jinja2 template"""
  t = jinja_env.get_template(template)
  return t.render(params)

def report_upload(repo_path, xml_filepath, jasper_url, username, password, datasource_path,query_path):
  
  template = "inputcontrol_res_desc.xml"
  auth = (username, password)    
  
  (parent_folder, report_name) = repo_path.rsplit('/', 1)

  tree = ET.parse(xml_filepath)

  queryValueColumn = ''
  queryVisibleColumn = ''
  version = (tree.findall('./version'))[0].text
  inputcontrol_type = (tree.findall('./type'))[0].text  
  report_label = (tree.findall('./label'))[0].text
  queryModel = ''

  #QueryModel for InputQuery and Query Resource
  if tree.findall('./query/localResource'):
    queryValueColumn = (tree.findall('./queryValueColumn'))[0].text
    queryVisibleColumn = (tree.findall('./queryVisibleColumn'))[0].text
    query_name = (tree.findall('./query/localResource/name'))[0].text
    query_label = (tree.findall('./query/localResource/label'))[0].text
    repo_query_path = repo_path + '_files/'+query_name
    query_parent_folder = repo_path + '_files'
    query_version = (tree.findall('./query/localResource/version'))[0].text
    query_String = (tree.findall('./query/localResource/queryString'))[0].text
    query_language = (tree.findall('./query/localResource/language'))[0].text
    query_uri = datasource_path

    queryModel = '''
    <resourceDescriptor name="'''+query_name+'''" wsType="query" uriString="'''+repo_query_path+'''" isNew="false">
		<label><![CDATA['''+query_label+''']]></label>
		<resourceProperty name="PROP_RESOURCE_TYPE">
			<value><![CDATA[com.jaspersoft.jasperserver.api.metadata.common.domain.Query]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_PARENT_FOLDER">
			<value><![CDATA['''+query_parent_folder+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_VERSION">
			<value><![CDATA['''+query_version+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_SECURITY_PERMISSION_MASK">
			<value><![CDATA[1]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_HAS_DATA">
			<value><![CDATA[false]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_IS_REFERENCE">
			<value><![CDATA[false]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_QUERY">
			<value><![CDATA['''+query_String+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_QUERY_LANGUAGE">
			<value><![CDATA['''+query_language+''']]></value>
		</resourceProperty>
		<resourceDescriptor wsType="datasource" isNew="false">
			<resourceProperty name="PROP_REFERENCE_URI">
				<value><![CDATA['''+query_uri+''']]></value>
			</resourceProperty>
			<resourceProperty name="PROP_IS_REFERENCE">
				<value><![CDATA[true]]></value>
			</resourceProperty>
		</resourceDescriptor>
	</resourceDescriptor>'''

  if tree.findall('./query/uri'):
    
    query_repo_path = query_path + '/'+os.path.basename((tree.findall('./query/uri'))[0].text)
    queryValueColumn = (tree.findall('./queryValueColumn'))[0].text
    queryVisibleColumn = (tree.findall('./queryVisibleColumn'))[0].text
    
    queryModel = '''
    <resourceDescriptor wsType="reference" isNew="false">
			<resourceProperty name="PROP_REFERENCE_URI">
				<value><![CDATA['''+query_repo_path+''']]></value>
			</resourceProperty>
			<resourceProperty name="PROP_IS_REFERENCE">
				<value><![CDATA[true]]></value>
			</resourceProperty>
	</resourceDescriptor>
		'''
    
  if tree.findall('./dataType'):
    Dt_Name = (tree.findall('./dataType/localResource/name'))[0].text
    Dt_Parent_Folder = repo_path + '_files/'
    Dt_uri = repo_path + '_files/' +os.path.basename((tree.findall('./dataType/localResource/folder'))[0].text)
    Dt_label_Name = (tree.findall('./dataType/localResource/label'))[0].text
    Dt_Type = (tree.findall('./dataType/localResource/type'))[0].text
    Dt_Max_Value = (tree.findall('./dataType/localResource/maxValue'))[0].text
    Dt_Min_Value = (tree.findall('./dataType/localResource/minValue'))[0].text
    Dt_Max_Strict = (tree.findall('./dataType/localResource/strictMax'))[0].text
    Dt_Min_Strict = (tree.findall('./dataType/localResource/strictMin'))[0].text

    
    queryModel = '''
                <resourceDescriptor name="'''+Dt_Name+'''" wsType="dataType" uriString="'''+Dt_uri+'''" isNew="false">
		<label><![CDATA['''+Dt_label_Name+''']]></label>
		<resourceProperty name="PROP_RESOURCE_TYPE">
			<value><![CDATA[com.jaspersoft.jasperserver.api.metadata.common.domain.DataType]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_PARENT_FOLDER">
			<value><![CDATA['''+Dt_Parent_Folder+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_VERSION">
			<value><![CDATA[0]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_SECURITY_PERMISSION_MASK">
			<value><![CDATA[1]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_HAS_DATA">
			<value><![CDATA[false]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_IS_REFERENCE">
			<value><![CDATA[false]]></value>
		</resourceProperty>
		<resourceProperty name="PROP_DATATYPE_TYPE">
			<value><![CDATA['''+Dt_Type+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_DATATYPE_MAX_VALUE">
			<value><![CDATA['''+Dt_Max_Value+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_DATATYPE_MIN_VALUE">
			<value><![CDATA['''+Dt_Min_Value+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_DATATYPE_STRICT_MAX">
			<value><![CDATA['''+Dt_Max_Strict+''']]></value>
		</resourceProperty>
		<resourceProperty name="PROP_DATATYPE_STRICT_MIN">
			<value><![CDATA['''+Dt_Min_Strict+''']]></value>
		</resourceProperty>
	</resourceDescriptor>
                '''


  
  args ={
  'repo_path': repo_path.strip().rstrip('/'),
  'report_name': report_name,
  'parent_folder': parent_folder,
  
  'queryValueColumn' : queryValueColumn,
  'queryVisibleColumn' : queryVisibleColumn,
  
  'version' : version,
  'inputcontrol_type' : inputcontrol_type,
  'report_label' : report_label,
  'queryModel' : queryModel,
  'jasper_url': jasper_url.strip().rstrip('/'),
  'rest_resource': '/rest/resource',
  'auth': auth
  }
  
  #we cannot initialize some values from other values before they are initilized 
  args['url'] = args['jasper_url'] + args['rest_resource'] + args['repo_path']
  
  #render template   
  try:  
    resource_descriptor = render_template(template, **args)
  except:
    raise
  #open jrxml file
  open("InputElement_log.txt", "w")
  try:
    upload = open('InputElement_log.txt', 'rb')
  except:
    raise   
  
  #Initialize ResourceDescriptor from rendered template
  args['data'] = {"ResourceDescriptor": resource_descriptor }
  
  #Initialize files. Name should be args['report_files_path'] for request to work 
  args['files'] = {'/': (args['report_name'], upload),
             }
  #making actual request 
  r = requests.put(url=args['url'], data=args['data'], files=args['files'], auth=args['auth'])
  
  #logging
  logging.info(r.status_code)
  r.raise_for_status()
  os.remove("InputElement_log.txt")
  
