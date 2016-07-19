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

def report_upload(repo_path, datasource_filepath, jasper_url, username, password ,env_connectionUrl ,env_connectionUser ,env_connectionPassword):
  
  template = "data_Source_res_desc.xml"
  auth = (username, password)    
  
  (parent_folder, report_name) = repo_path.rsplit('/', 1)

  tree = ET.parse(datasource_filepath)
  
  driver = (tree.findall('./driver'))[0].text
  connectionUrl = env_connectionUrl
  connectionUser = env_connectionUser
  connectionPassword = env_connectionPassword
  dbName = connectionUrl.rsplit('/', 1)[-1]
 
  args ={
  'repo_path': (parent_folder+'/'+dbName).strip().rstrip('/'),
  'report_name': dbName,
  'report_label': dbName,
  'parent_folder': parent_folder,
  
  'driver' : driver,
  'connectionPassword' : connectionPassword,
  'connectionUser' : connectionUser,
  'connectionUrl' : connectionUrl,
    
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
  open("datasource_log.txt", "w")
  try:
    upload = open('datasource_log.txt', 'rb')
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
  os.remove("datasource_log.txt")
  return dbName
