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

def report_upload(repo_path, xml_filepath, jasper_url, username, password, datasource_path):
  
  template = "query_res_desc.xml"
  auth = (username, password)    
  
  (parent_folder, report_name) = repo_path.rsplit('/', 1)

  tree = ET.parse(xml_filepath)
  
  report_label = (tree.findall('./label'))[0].text
  query_version = (tree.findall('./version'))[0].text
  query_string = (tree.findall('./queryString'))[0].text
  query_language = (tree.findall('./language'))[0].text
  report_datasource = datasource_path
 
  args ={
  'repo_path': repo_path.strip().rstrip('/'),
  'report_name': report_name,
  'parent_folder': parent_folder,
  'report_label' : report_label,
  'query_version' : query_version,
  'query_string' : query_string,
  'query_language' : query_language,
  'report_datasource' : report_datasource,
  
  
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
  open("Query_log.txt", "w")
  try:
    upload = open('Query_log.txt', 'rb')
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
  os.remove("Query_log.txt")
  
