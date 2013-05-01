def get_keys(bamboo_entity, entity_type):
  entity_list = bamboo_entity[entity_type+'s'][entity_type]
  return map(lambda d: d['key'], entity_list)


