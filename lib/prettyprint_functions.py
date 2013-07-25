
def print_build_results(res, filter_func=lambda x: True):
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

def print_ls(l):
  for item in l:
    print item
