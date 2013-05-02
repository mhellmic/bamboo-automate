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
