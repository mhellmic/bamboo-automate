import cookielib
import logging
import re
from .. import requests
import urllib2

def _test_authentication(conn):
  requests.get_ui_return_html(
      conn,
      conn.baseurl,
      {})

def external_authenticate(host, cookiefile, baseurl=''):
  retrieval_cookiejar = cookielib.MozillaCookieJar()
  retrieval_cookiejar.load(cookiefile, ignore_discard=True, ignore_expires=True)

  auth_cookies = []
  for c in retrieval_cookiejar:
    if re.search(c.domain, host):
      if re.search('JSESSIONID', c.name):
        logging.debug('%s %s %s', c.domain, c.name, c.value)
        auth_cookies.append(c)
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
