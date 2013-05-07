def _get_value_from_bamboo_dict(bamboo_dict, dict_type, type_value):
  entity_list = bamboo_dict[dict_type+'s'][dict_type]
  return map(lambda d: d[type_value], entity_list)

def get_keys(bamboo_dict, dict_type):
  return _get_value_from_bamboo_dict(bamboo_dict,
                                     dict_type,
                                     'key')
def get_project_keys(bamboo_dict):
  return _get_value_from_bamboo_dict(bamboo_dict,
                                     'project',
                                     'key')

def get_plan_keys(bamboo_dict):
  return _get_value_from_bamboo_dict(bamboo_dict,
                                     'plan',
                                     'key')

def order_tasks_in_list(list_dict):
  res_list = []
  for key, value in list_dict.iteritems():
    res_list.append((key, value[0], value[4],))

  return sorted(res_list, key=lambda t: t[2])

def _correct_permission_usertype(usertype):
  if usertype == 'other':
    return 'role'
  else:
    return usertype

def _correct_permission_username(username):
  if username == 'Logged in Users':
    return 'ROLE_USER'
  elif username == 'Anonymous Users':
    return 'ROLE_ANONYMOUS'
  else:
    return username

def _correct_permission_type(ptype):
  if ptype == 'admin':
    return 'administration'
  else:
    return ptype

def parse_permission_params(params_dict):
  params = {}
  for pusertype, pusertype_val in params_dict.iteritems():
    usertype = _correct_permission_usertype(pusertype)
    for puser, pperms in pusertype_val.iteritems():
      username = _correct_permission_username(puser)
      for ptype, pval in pperms.iteritems():
        permtype = _correct_permission_type(ptype)
        if pval:
          perm_string = '_'.join(['bambooPermission',
                                  usertype,
                                  username,
                                  permtype.upper()])
          params[perm_string] = 'on'

  return params

