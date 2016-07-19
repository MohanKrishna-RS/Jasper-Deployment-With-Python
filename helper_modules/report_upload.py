#!/bin/etc/python
import requests

import argparse

import logging
import httplib
import jinja2
#jinja2 used for templating report uploads
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def render_template(template, **params):
  """Return rendered jinja2 template"""
  t = jinja_env.get_template(template)
  return t.render(params)

def report_upload(repo_path, report_jrxml, report_datasource, jasper_url, user, password ,report_label, subreport_list):

  template = "report_res_descr_temp.xml"
  auth = (user, password)    
  
  #really basic stripping, use something else for production
  
  (parent_folder, report_name) = repo_path.rsplit('/', 1)
    
  args ={
  'repo_path': repo_path.strip().rstrip('/'),
  'report_name': report_name,
  'report_label':report_label,
  'parent_folder': parent_folder,
  'report_jrxml': report_jrxml.strip().rstrip('/'),
  'report_datasource': report_datasource.strip().rstrip('/'),
  'jasper_url': jasper_url.strip().rstrip('/'),
  'rest_resource': '/rest/resource',
  'auth': auth
  }
  
  args['url'] = args['jasper_url'] + args['rest_resource'] + args['repo_path']
  #required for request and Jinja2 template
  args['report_files_path'] = args['repo_path'] +  "_files/" +  report_name + "_jrxml"
  
  #render template   
  try:  
    resource_descriptor = render_template(template, **args)
  except:
    raise
  
  #open jrxml file
  try:
    upload = open(args['report_jrxml'], 'rb')
  except:
    raise   
  
  #Initialize ResourceDescriptor from rendered template
  args['data'] = {"ResourceDescriptor": resource_descriptor }
  
  #Initialize files. Name should be args['report_files_path'] for request to work 
  args['files'] = {args['report_files_path']: (args['report_name'], upload),
             }

  #Adding Sub Reports
  for subreport in subreport_list:
    sub_name = os.path.basename(subreport)
    sub_data = open(subreport+'.data', 'rb')
    args['files'].update({
      args['repo_path'] +  "_files/" + sub_name :\
      (str(sub_name.split('.')[0]), sub_data)
      })
  
  #making actual request 
  r = requests.put(url=args['url'], data=args['data'], files=args['files'], auth=args['auth'])
  
  #logging
  logging.info(r.status_code)
  r.raise_for_status()                
