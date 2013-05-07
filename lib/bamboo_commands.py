import cookielib
import logging
from publicsuffix import PublicSuffixList
import re
import requests
import time
import urllib2

logging.basicConfig(level=logging.DEBUG)

def _test_authentication(conn):
  requests.get_ui_return_html(
      conn,
      conn.baseurl,
      {})

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

  _test_authentication(conn)
  logging.debug('authentication test successful')

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

def delete_plan_variable(conn, plan_id, var_key):
  var_id = _find_variable_id(conn, plan_id, var_key)
  logging.debug('%s', var_id)

  params = {
      "planKey": plan_id,
      "variableId": var_id
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/deletePlanVariable.action',
      params)

  return res

def _delete_plan_variable_by_id(conn, plan_id, var_id):
  logging.debug('%s', var_id)

  params = {
      "bamboo.successReturnMode": "json",
      "confirm": "true",
      "decorator": "nothing",
      "planKey": plan_id,
      "variableId": var_id
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/deletePlanVariable.action',
      params)

  return res

def delete_plan_all_variables(conn, plan_id):
  variables = _find_all_variables(conn, plan_id)
  for var_id in variables.itervalues():
    logging.debug(var_id)
    res = _delete_plan_variable_by_id(conn, plan_id, var_id)

def _find_all_variables(conn, plan_id):
  params = {
      "buildKey": plan_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/configureChainVariables.action',
      params)

  variables = {}

  match_key = re.compile('key_(\d+)')
  root = res #.getroot()
  span_varid = root.find_class('inline-edit-field text')
  for v in span_varid:
    m = match_key.match(v.name)
    if m:
      variables[v.value] = m.group(1)

  return variables

def _find_variable_id(conn, plan_id, var_key):
  variables = _find_all_variables(conn, plan_id)
  return variables[var_key]

def get_jobs(conn, plan_key, sort_by_title=False):
  params = {
      "buildKey": plan_key
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/editChainDetails.action',
      params)

  root = res #.getroot()

  jobs = {}
  li_jobkeys = root.findall('.//li[@data-job-key]')
  for li in li_jobkeys:
    key = li.attrib['data-job-key']
    edit_link = li.find('.//a').attrib['href']
    del_link = None
    title = li.find('.//a').text
    description = None
    try:
      description = li.attrib['title']
    except:
      pass

    if sort_by_title:
      jobs[title] = (key, description, edit_link, del_link,)
    else:
      jobs[key] = (title, description, edit_link, del_link,)

  return jobs

  li_jobkeys = root.findall('.//li[data-job-key=".*"]')
  logging.debug('%s', li_jobkeys)

def get_tasks(conn, job_id, sort_by_title=False):
  params = {
      "buildKey": job_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/editBuildTasks.action',
      params)

  root = res #.getroot()

  tasks = {}

  li_items = root.find_class('item')
  for order_id, li in enumerate(li_items, start=1):
    key = int(li.attrib['data-item-id'])
    edit_link = None
    del_link = None
    title = li.find('.//h3').text
    description = None
    try:
      description = li.find('.//div').text
    except:
      pass
    links = li.findall('.//a')
    for l in links:
      href = l.attrib['href']
      match = re.search('editTask', href)
      if match:
        edit_link = href
      match = re.search('confirmDeleteTask', href)
      if match:
        del_link = href
        req_id = href

    if sort_by_title:
      title_desc = (title, description)
      tasks[title_desc] = (key, (title, description), edit_link, del_link, order_id,)
    else:
      tasks[key] = (title, description, edit_link, del_link, order_id,)

  return tasks


def _get_requirements(conn, job_id):
  params = {
      "buildKey": job_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/defaultBuildRequirement.action',
      params)

  root = res #.getroot()

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
  logging.debug(params)
  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/addBuildRequirement.action',
      params)

  return res

def delete_job_task(conn, job_id, task_id):
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": job_id,
      "confirm": "true",
      "createTaskKey": None,
      "decorator": "nothing",
      "taskId": task_id
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/edit/deleteTask.action',
      params)

  return res

def move_job_task(conn, job_id, task_id, finalising=False, beforeId=None, afterId=None):
  """ Move a task in the runtime order.

  Arguments:
  conn -- the connection object
  job_id -- the id of the job
  task_id -- the id of the task to move
  finalising -- true, if task should be a final task
  beforeId -- id of the task which should be before this task
  afterId -- id of the task which should be after this taks

  """
  params = {
      "planKey": job_id,
      "finalising": "true" if finalising else "false",
      "taskId": task_id
      }
  if beforeId:
    params.update({"beforeId": beforeId})
  if afterId:
    params.update({"afterId": afterId})
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/moveTask.action',
      params)

  return res

def add_job_task(conn, job_id, task_id, task_params):
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": job_id,
      "checkBoxFields": "taskDisabled",
      "confirm": "true",
      "createTaskKey": task_id,
      "decorator": "nothing",
      "taskId": 0,
      "finalising": "true",
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

def _get_entity(conn, entity, expand):
  params = {
      "expand": expand
      }
  res = requests.get_rest_return_json(
      conn,
      conn.baseurl+'/rest/api/latest/'+entity,
      params)

  return res

def get_plans(conn, expand=''):
  params = {
      "expand": expand
      }
  res = _iterate_json_plan_results(
      requests.get_ui_return_json,
      conn,
      conn.baseurl+'/rest/api/latest/plan',
      params)

  return res

def get_projects(conn, expand=''):
  return _get_entity(conn, 'project', expand)

def _check_permission(html_root, usertype, username, permission):
  if usertype == 'other':
    usertype = 'role'
  if username == 'Logged in Users':
    username = 'ROLE_USER'
  elif username == 'Anonymous Users':
    username = 'ROLE_ANONYMOUS'
  permission_input_field_name = 'bambooPermission_'+usertype+'_'+username+'_'+permission.upper()
  permission_cell_name = permission_input_field_name+'_cell'
  permission_xpath = './/td[@id="'+permission_cell_name+'"]/input[@name="'+permission_input_field_name+'"]'
  logging.debug('xpath to search for permission checkbox = %s' % permission_xpath)
  el = html_root.find(permission_xpath)
  if el == None:
    logging.debug('element not found')
    return False
  logging.debug('element is checked = %s', True if 'checked' in el.attrib else False)
  if 'checked' in el.attrib:
    return True
  else:
    return False

def _get_type_permissions(html_root, usertype):
  table_user = html_root.findall('.//table[@id="configureBuild'+usertype.capitalize()+'Permissions"]/tr')
  logging.debug('xpath to search for permission table = %s' % table_user)

  user_permissions = {}

  for tr in table_user:
    key = None
    try:
      key = tr.find('td[1]/a').attrib['href'].rsplit('/',1)[1]
    except:
      key = tr.find('td[1]').text
    read_p = _check_permission(tr, usertype, key, 'READ')
    write_p = _check_permission(tr, usertype, key, 'WRITE')
    build_p = _check_permission(tr, usertype, key, 'BUILD')
    clone_p = _check_permission(tr, usertype, key, 'CLONE')
    admin_p = _check_permission(tr, usertype, key, 'ADMINISTRATION')

    user_permissions[key] = {'read':read_p,
                             'write':write_p,
                             'build':build_p,
                             'clone':clone_p,
                             'admin':admin_p}

  return user_permissions

def get_plan_permissions(conn, plan_id):
  params = {
      "buildKey": plan_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/editChainPermissions.action',
      params)

  root = res #.getroot()

  user_permissions = _get_type_permissions(root, 'user')
  group_permissions = _get_type_permissions(root, 'group')
  other_permissions = _get_type_permissions(root, 'other')

  return {'user': user_permissions,
          'group': group_permissions,
          'other': other_permissions}


def mod_plan_permissions(conn, plan_id, permission_params):
  params = {
      "buildKey": plan_id,
      "newGroup": None,
      "newUser": None,
      "principalType": "User",
      "save": "Save",
      "selectFields": "principalType"
      }
  params.update(permission_params)
  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/updateChainPermissions.action',
      params)

  return res
