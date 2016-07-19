#!/bin/etc/python
import requests
import argparse
import logging
import httplib
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def render_template(template, **params):
  """Return rendered jinja2 template"""
  t = jinja_env.get_template(template)
  return t.render(params)

def create_folder(jasper_url,username,password,folder_path):

  auth = (username, password)
  open("folder_log.txt", "w") 

  (parent_folder, folder_name) = folder_path.rsplit('/', 1)

  args ={
  'folder_path': folder_path.strip().rstrip('/'),
  'folder_name': folder_name,
  'parent_folder': parent_folder,
  'jasper_url': jasper_url.strip().rstrip('/'),
  'rest_resource': '/rest/resource',
  'auth': auth
  }
  args['url'] = args['jasper_url'] + args['rest_resource'] + args['folder_path']

  
        
  #render template   
  try:  
       resource_descriptor = render_template("folder_res_desc.xml", **args)
  except:
       raise

  #open jrxml file
  try:
       upload = open("folder_log.txt", 'rb')
  except:
       raise

  #Initialize ResourceDescriptor from rendered template
  args['data'] = {"ResourceDescriptor": resource_descriptor }

  #Initialize files. Name should be args['report_files_path'] for request to work 
  args['files'] = {'/': (args['folder_name'], upload)}

  #making actual request 
  r = requests.put(url=args['url'], data=args['data'], files=args['files'], auth=args['auth'])

  #logging
  logging.info(r.status_code)
  r.raise_for_status()
  os.remove("folder_log.txt")
  return

