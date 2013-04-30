import cookielib
import logging
from publicsuffix import PublicSuffixList
import re
import requests
import time
import urllib2

logging.basicConfig(level=logging.DEBUG)

def external_authenticate(host, cookiefile, baseurl=''):
  retrieval_cookiejar = cookielib.MozillaCookieJar()
  retrieval_cookiejar.load(cookiefile, ignore_discard=True, ignore_expires=True)

  auth_cookies = []
  psl = PublicSuffixList()
  host_publicsuffix = psl.get_public_suffix(host)
  for c in retrieval_cookiejar:
    if re.search(host, c.domain):
      if re.search('JSESSIONID', c.name):
        logging.debug('%s %s %s', c.domain, c.name, c.value)
        auth_cookies.append(c)
    elif re.search(host_publicsuffix, c.domain):
      if re.search('crowd.token_key', c.name):
        logging.debug('%s %s %s', c.domain, c.name, c.value)
        auth_cookies.append(c)

  cookiejar = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
  conn = requests.Connection(host, baseurl, opener, cookiejar)
  conn.auth_cookies = auth_cookies

  return conn

def authenticate(host, user, passwd, baseurl=''):
  cookiejar = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
  conn = requests.Connection(host, baseurl, opener, cookiejar)

  creds = {
      "os_username": user,
      "os_password": passwd
      }
  requests.post_ui_no_return(
      conn,
      conn.baseurl+'/userlogin!default.action',
      creds)

  return conn

def add_plan_variable(conn, plan_id, var_key, var_value):
  params = {
      "planKey": plan_id,
      "variableKey": var_key,
      "variableValue": var_value
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/createPlanVariable.action',
      params)

  return res

def mod_plan_variable(conn, plan_id, var_key, var_value):
  var_id = _find_variable_id(conn, plan_id, var_key)
  logging.debug('%s', var_id)

  params = {
      "planKey": plan_id,
      "variableId": var_id,
      "variableKey": var_key,
      "variableValue": var_value
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/updatePlanVariable.action', 
      params)

  return res

def add_mod_plan_variable(conn, plan_id, var_key, var_value):
  res = add_plan_variable(conn, plan_id, var_key, var_value)
  if res['status'] == 'ERROR':
    if 'This Plan already contains a variable named '+var_key in res['fieldErrors']['variableKey']:
      res = mod_plan_variable(conn, plan_id, var_key, var_value)

  return res

def _find_variable_id(conn, plan_id, var_key):
  params = {
      "buildKey": plan_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/configureChainVariables.action',
      params)

  match_key = re.compile('key_(\d+)')
  root = res.getroot()
  variables = root.find_class('inline-edit-field text')
  for v in variables:
    if v.value == 'automate':
      m = match_key.match(v.name)
      if m:
        return m.group(1)
      else:
        return None 

def _get_requirements(conn, job_id):
  params = {
      "buildKey": job_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/defaultBuildRequirement.action',
      params)

  root = res.getroot()

  requirements = {}

  td_labels = root.find_class('labelCell')
  for td in td_labels:
    key = None
    req_id = None
    edit_link = None
    del_link = None
    tr = td.getparent()
    links = tr.findall('.//a')
    for l in links:
      href = l.attrib['href']
      match = re.search('capabilityKey=(.*)', href)
      if match:
        key = match.group(1)
      match = re.search('editBuildRequirement.*requirementId=(\d+)', href)
      if match:
        edit_link = href
        req_id = match.group(1)
      match = re.search('deleteBuildRequirement.*requirementId=(\d+)', href)
      if match:
        del_link = href
        req_id = match.group(1)

    if not key:
      key = td.text.strip()

    requirements[key] = (req_id, edit_link, del_link,)

  return requirements

def delete_job_requirement(conn, job_id, req_key):
  requirements = _get_requirements(conn, job_id)
  logging.debug('%s', requirements)
  res = None
  req_id, _, del_link = requirements[req_key]
  if req_id != None:
    res = requests.post_ui_no_return(conn, del_link, {})

  return res

def delete_job_all_requirements(conn, job_id):
  requirements = _get_requirements(conn, job_id)
  res = None
  for req_id, _, del_link in requirements.itervalues():
    if req_id != None:
      res = requests.post_ui_no_return(conn, del_link, {})

  return res

def add_job_requirement(conn, job_id, req_key, req_value, req_exists=False):
  params = {
      "Add": "Add",
      "buildKey": job_id,
      "existingRequirement": req_key if req_exists else None,
      "regexMatchValue": None,
      "requirementKey": None if req_exists else req_key,
      "requirementMatchType": "equal",
      "requirementMatchValue": req_value,
      "selectFields": "existingRequirement",
      "selectFields": "requirementMatchType"
      }
  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/addBuildRequirement.action',
      params)

  return res

def add_job_task(conn, job_id, task_key, task_params):
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": job_id,
      "checkBoxFields": "taskDisabled",
      "confirm": "true",
      "createTaskKey": task_key,
      "decorator": "nothing",
      "referer": "/build/admin/edit/editBuildTasks.action?buildKey=LCGDM-PUPPET-JOB1",
      "taskId": 0,
      "userDescription": None
      }
  params.update(task_params)
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/edit/createTask.action',
      params)

  return res

def _iterate_json_plan_results(request, conn, path, params):
  start_index = 0
  params.update({
    "start-index": start_index
    })
  res = request(conn, path, params)
  logging.debug('%s', res['plans']['max-result'])
  part_res = res
  while part_res['plans']['max-result'] >= 25:
    logging.debug('%s', part_res['plans']['max-result'])
    start_index = start_index + 25
    params.update({
      "start-index": start_index
      })
    part_res = request(conn, path, params)
    res['plans']['plan'].extend(part_res['plans']['plan'])

  return res

def get_plans(conn):
  params = {}
  res = _iterate_json_plan_results(
      requests.get_ui_return_json,
      conn,
      conn.baseurl+'/rest/api/latest/plan.json',
      params)

  return res

def get_plan_keys(conn):
  plans = get_plans(conn)['plans']['plan']
  return map(lambda d: d['key'], plans)
