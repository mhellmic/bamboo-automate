
def print_build_results(res, filter_func=lambda x: True):
  {u'number': 13, u'state': u'Failed', u'link': {u'href': u'http://localhost:6990/bamboo/rest/api/latest/result/LCGDM-PUPPET-13', u'rel': u'self'}, u'plan': {u'name': u'lcgdm - puppet', u'enabled': True, u'link': {u'href': u'http://localhost:6990/bamboo/rest/api/latest/plan/LCGDM-PUPPET', u'rel': u'self'}, u'key': u'LCGDM-PUPPET', u'shortName': u'puppet', u'shortKey': u'PUPPET', u'type': u'chain'}, u'key': u'LCGDM-PUPPET-13', u'id': 2523137, u'lifeCycleState': u'Finished'}
  build_list = res['results']['result']
  print '=================================='
  print ' Build results:'
  print ' key\tstate\tlink'
  print '=================================='
  for build in filter(filter_func, build_list):
    print ' %(build_key)s\t%(build_state)s\t%(build_link)s' % {
        'build_key': build['key'],
        'build_state': build['state'],
        'build_link': build['link']['href']
        }

