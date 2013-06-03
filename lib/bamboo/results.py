import logging
from .. import requests

def get_build_results(conn, project_key=None, expand=''):
  params = {
      "expand": expand
      }
  entity = "result/"+project_key if project_key else "result"
  res = requests.get_rest_return_json(
      conn,
      conn.baseurl+'/rest/api/latest/'+entity,
      params)

  return res

