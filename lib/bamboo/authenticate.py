import cookielib
import logging
import re
from .. import requests
import urllib2


def _test_authentication(conn):
  """ Tests if the authentication was successful

  The first assumption is that the bamboo server uses an external
  authentication system. If the returned url is from the bamboo
  server, we assume authentication has succeeded, if it is not
  we assume we have been redirected to login again.
  The other hint we take into account is getting redirected to
  the bamboo login page again when bamboo-internal auth is used.

  This function is likely to give false positives in other
  deployments.

  """
  page, url, http_code = requests.get_ui_return_html_status(
      conn,
      conn.baseurl,
      {})
  if (re.search(conn.host, url) is not None and
          re.search('userlogin', url) is None):
    return True
  else:
    return False


def external_authenticate(host, cookiefile, baseurl=''):
  retrieval_cookiejar = cookielib.MozillaCookieJar()
  retrieval_cookiejar.load(cookiefile,
                           ignore_discard=True,
                           ignore_expires=True)

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

  if _test_authentication(conn):
    logging.debug('authentication test successful')
    conn.connected = True
  else:
    logging.debug('authentication test failed')
    conn.connected = False

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
      conn.baseurl + '/userlogin!default.action',
      creds)

  if _test_authentication(conn):
    logging.debug('authentication test successful')
    conn.connected = True
  else:
    logging.debug('authentication test failed')
    conn.connected = False

  return conn
