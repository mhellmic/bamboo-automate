import logging
from .. import requests

def _iterate_json_entity_results(request, conn, entity, path, params):
  start_index = 0
  params.update({
    "start-index": start_index
    })
  entities = entity+'s'
  res = request(conn, path, params)
  logging.debug('%s', res[entities]['max-result'])
  part_result_size = res[entities]['max-result']
  result_size = res[entities]['size']
  part_res = res
  while start_index <= result_size:
    logging.debug('size = %s max-result = %s', res[entities]['size'], res[entities]['max-result'])
    logging.debug('start_index = %s', start_index)
    start_index = start_index + part_result_size
    params.update({
      "start-index": start_index
      })
    part_res = request(conn, path, params)
    res[entities][entity].extend(part_res[entities][entity])

  return res

def _get_entity(conn, entity, expand):
  params = {
      "expand": expand
      }
  res = _iterate_json_entity_results(
      requests.get_rest_return_json,
      conn,
      entity,
      conn.baseurl+'/rest/api/latest/'+entity,
      params)

  return res

def get_plans(conn, expand=''):
  return _get_entity(conn, 'plan', expand)

def get_projects(conn, expand=''):
  return _get_entity(conn, 'project', expand)
