from functools import wraps
from lxml import html
import json
import logging
import re
import time
import urllib
import urllib2


MAXRETRIES = 3
RETRYSLEEP = 5


class Connection:
  def __init__(self, hostname, baseurl, opener, auth_cookies):
    self.host = hostname
    self.opener = opener
    self.auth_cookies = auth_cookies
    self.baseurl = baseurl
    self.connected = False

def get_ui_return_html_status(conn, path, params):
  page, url, http_code = _request(conn, "GET", path, params, [], urllib.urlencode, html.fromstring)
  return page, url, http_code

def get_ui_return_html(conn, path, params):
  res, _, _ = _request(conn, "GET", path, params, [], urllib.urlencode, html.fromstring)
  return res

def get_ui_return_json(conn, path, params):
  headers = [('Accept', 'application/json')]
  try:
    res, _, _ = _request(conn, "GET", path, params, headers, urllib.urlencode, json.loads)
  except:
    res = {'status':'NotOK'}
  return res

def post_ui_no_return(conn, path, params):
  res,_ , _ = _request(conn, "POST", path, params, [], urllib.urlencode, id)

def post_ui_return_html(conn, path, params):
  res, _, _ = _request(conn, "POST", path, params, [], urllib.urlencode, html.fromstring)
  return res

def post_ui_return_json(conn, path, params):
  headers = [('Accept', 'application/json')]
  try:
    res, _, _ = _request(conn, "POST", path, params, headers, urllib.urlencode, json.loads)
  except:
    res = {'status':'NotOK'}
  return res

def get_rest_return_json(conn, path, params):
  return get_ui_return_json(conn, path, params)

def post_rest_return_json(conn, path, params):
  return get_ui_return_json(conn, path, params)

rolling_avg_counter = 1
rolling_avg_list = []
rolling_avg = 0
def monitoring(func):
  @wraps(func)
  def with_time_monitoring(*args, **kwargs):
    global rolling_avg_counter, rolling_avg_list, rolling_avg
    t1 = time.time()
    time.sleep(3.0)
    t2 = time.time()
    logging.debug('slept %(sleep)s seconds.' % {'sleep': (t2 - t1)})
    start_time = time.time()
    res = func(*args, **kwargs)
    end_time = time.time()
    logging.debug('%(fname)s took %(dur)s.' % {'fname': func.__name__,
                                               'dur': (end_time - start_time)})

    rolling_avg_counter += 1
    rolling_avg_list.append(end_time - start_time)
    if rolling_avg_counter % 10 == 0:
      rolling_avg_counter = 1
      rolling_avg = ((rolling_avg + sum(rolling_avg_list)) /
                     (1 + len(rolling_avg_list)))
      rolling_avg_list = []
      logging.debug('%(fname)s rolling average is %(dur)s.'
                    % {'fname': func.__name__,
                       'dur': rolling_avg})

    return res
  return with_time_monitoring

@monitoring
def _request(conn, method, path, params, headers, param_parse_func, response_parse_func):
  path_and_params = None
  if method == "GET":
    path_and_params = path+'?'+urllib.urlencode(params) if params else path
  else:
    path_and_params = path

  req = urllib2.Request(conn.host+path_and_params)
  for key, value in headers:
    req.add_header(key, value)

  cookies = []
  for c in conn.auth_cookies:
    cookies.append(c.name+'='+c.value.strip())

  cookies = '; '.join(cookies)
  if len(cookies) > 0:
    req.add_header('Cookie', cookies)

  retries = 0
  req_success = False
  while not req_success:
    logging.debug('%s', req.get_full_url())
    try:
      if method == "POST":
        response = conn.opener.open(req, param_parse_func(params))
      elif method == "GET":
        response = conn.opener.open(req)
      req_success = True
    except urllib2.URLError:
      if retries >= MAXRETRIES:
        raise
      time.sleep(RETRYSLEEP)
    finally:
      retries += 1

  logging.debug('%s %s', response.geturl(), response.getcode())
  if response.getcode() > 399:
    raise urllib2.HTTPError(code=response.getcode())

  response_content = response.read()
  try:
    res = response_parse_func(response_content)
  except:
    logging.debug('The response content follows:')
    logging.debug(response_content)
    logging.debug('End of response content.')
    raise

  return res, response.geturl(), response.getcode()
