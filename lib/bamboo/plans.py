import logging
from .. import requests

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
