from bamboo_commands import *
from manipulate_bamboo_json import *
import re
from types import *

def change_plan_permission(conn, plan_key, permission):
  """ Change a single permission for a plan.

  Changes a permission provided its description as a three-tuple
  (usertype, username, permissiontype, value).
  It gets the current permissions on the plan, changes the permission
  and updates the plan.
  Note that _all_ permissions have to be send to bamboo, not only the
  changing ones. This function provides a safe interface.

  Since the function receives the current on every invocation, it is not
  efficient to use for changing many permissions.

  """
  assert type(permission) is TupleType, 'permission argument is not a tuple: %(t)r' % {'t':permission}
  assert len(permission) == 4, 'permission tuple does not have four values: %(t)r' % {'t':permission}
  assert type(permission[0]) is StringType, 'permission tuple\'s first value is not type string: %(t)r' % {'t':permission[0]}
  assert type(permission[1]) is StringType, 'permission tuple\'s second value is not type string: %(t)r' % {'t':permission[1]}
  assert type(permission[2]) is StringType, 'permission tuple\'s third value is not type string: %(t)r' % {'t':permission[2]}
  assert type(permission[3]) is BooleanType, 'permission tuple\'s fourth value is not type bool: %(t)r' % {'t':permission[3]}

  usertype, username, permissiontype, value = permission
  permissions = get_plan_permissions(conn, plan_key)
  try:
    if permissiontype == 'all':
      for key in permissions[usertype][username].iterkeys():
        permissions[usertype][username][key] = value
    else:
      permissions[usertype][username][permissiontype] = value
  except:
    logging.debug('Could not change permission: %(t)r' % {'t':permission})
    raise

  mod_plan_permissions(
      conn,
      plan_key,
      parse_permission_params(permissions))


def get_plans_in_project(conn, project_key, exclude_regex=None):
  """ Get all plans which belong to a project.

  This function updates the list of plans and filters it according
  to the provided project key. It can additionally filter the plan keys
  with the regex argument.

  Arguments:
  conn -- the connection
  project_key -- the project key to filter
  exclude_regex -- filter out plan with names that match this regex

  """
  plans = get_plans(conn, expand='plans.plan')
  project_plans = filter(lambda d:d['projectKey'] == project_key,
                         plans['plans']['plan'])

  exclude_regex = re.compile(exclude_regex)
  filtered_project_plans = filter(lambda d:exclude_regex.search(d['shortKey']) == None, project_plans)

  plans['plans']['plan'] = filtered_project_plans
  return plans

def move_task_to_position(conn, job_key, task_key, pos):
  """ Reorder a task list.

  Arguments:
  conn -- the connection
  tasks -- the task dict as given from bamboo
  task_key -- the key of the task to be positioned
  pos -- the position to put it, zero-indexed

  """
  res = None
  tasks = None
  task_id = None
  try:
    int(task_key)  # it's the ID, not the title
    tasks = get_tasks(conn, job_key)
    task_id = task_key
  except:          # it's the title
    assert type(task_key) is TupleType, 'task_key is neither int nor tuple: %(tk)r' % {'tk':task_key}
    tasks = get_tasks(conn, job_key, sort_by_title=True)
    task_id = tasks[task_key][0]

  assert type(task_id) is IntType, 'task_id is not an int: %(t)r' % {'t':task_id}

  tasks_sorted = order_tasks_in_list(tasks)
  task_id_before = None
  task_id_after = None

  try:
    task_id_before = tasks_sorted[pos-1][1]
    assert type(task_id_before) is IntType, 'task_id_before is not an int: %r' % task_id_before
  except:
    pass
  try:
    task_id_after = tasks_sorted[pos][1]
    assert type(task_id_before) is IntType, 'task_id_before is not an int: %r' % task_id_before
  except:
    pass

  if task_id_before and task_id_after:
    res = move_job_task(conn, job_key, task_id, beforeId=task_id_before, afterId=task_id_after)
  elif task_id_before:
    res = move_job_task(conn, job_key, task_key, beforeId=task_id_before)
  elif task_id_after:
    res = move_job_task(conn, job_key, task_key, afterId=task_id_after)
  else:
    print 'ERROR: moving task %(task)s to position %(pos)s failed.' % {'task': task_key, 'pos': pos }

  return res
