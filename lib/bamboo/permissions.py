import logging
from .. import requests

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
