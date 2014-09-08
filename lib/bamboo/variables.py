import logging
from .. import requests
import re

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
    logging.debug(res['fieldErrors']['variableKey'])
    if 'This plan already contains a variable named '+var_key in res['fieldErrors']['variableKey']:
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

  match_key = re.compile('key_(-?\d+)')
  root = res #.getroot()
  span_varid = root.find_class('inline-edit-field text')
  for v in span_varid:
    m = match_key.match(v.name)
    if m:
      variables[v.value] = m.group(1)

  return variables

def _find_variable_id(conn, plan_id, var_key):
  variables = _find_all_variables(conn, plan_id)
  logging.debug('all variables:\n'+str(variables))
  return variables[var_key]

