from lxml import html
import json
import re
import urllib
import urllib2

class Connection:
  def __init__(self, hostname, baseurl, opener, auth_cookies):
    self.host = hostname
    self.opener = opener
    self.auth_cookies = auth_cookies
    self.baseurl = baseurl

def get_ui_return_html(conn, path, params):
  res, _, _ = request(conn, path, params, [], urllib.urlencode, html.parse)
  return res

def post_ui_no_return(conn, path, params):
  res,_ , _ = request(conn, path, params, [], urllib.urlencode, id)

def post_ui_return_html(conn, path, params):
  res, _, _ = request(conn, path, params, [], urllib.urlencode, html.parse)
  return res

def post_ui_return_json(conn, path, params):
  headers = [('Accept', 'application/json')]
  res, _, _ = request(conn, path, params, headers, urllib.urlencode, json.load)
  return res

def request(conn, path, params, headers, param_parse_func, response_parse_func):
  req = urllib2.Request(conn.host+path)
  for key, value in headers:
    req.add_header(key, value)

  cookies = []
  for c in conn.auth_cookies:
    cookies.append(c.name+'='+c.value.strip())

  cookies = '; '.join(cookies)
  if len(cookies) > 0:
    req.add_header('Cookie', cookies)

  response = conn.opener.open(req, param_parse_func(params))
  res = response_parse_func(response)

  return res, response.geturl(), response.getcode()
