from manipulate_bamboo_json import *

from bamboo.authenticate import *
from bamboo.branches import *
from bamboo.jobs import *
from bamboo.permissions import *
from bamboo.plans import *
from bamboo.requirements import *
from bamboo.tasks import *
from bamboo.variables import *

import re
from types import *

def print_result(res, cmd, key):
  print '%(cmd)s %(key)s %(stat)s' % {'cmd': cmd, 'key': key,
      'stat': 'SUCCESS' if res['status'] == 'OK' else 'FAILED'}

def print_result_debug(res, cmd, key):
  logging.debug('%(cmd)s %(key)s %(stat)s' % {'cmd': cmd, 'key': key,
      'stat': 'SUCCESS' if res['status'] == 'OK' else 'FAILED'})

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
  except KeyError:
    logging.info('Could not change permission: %(t)r' % {'t':permission})
    return

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

  try:
    exclude_regex = re.compile(exclude_regex)
    filtered_project_plans = filter(lambda d:exclude_regex.search(d['shortKey']) == None, project_plans)
  except:
    filtered_project_plans = project_plans

  plans['plans']['plan'] = filtered_project_plans
  return plans

def move_task_to_position(conn, job_key, task_key, pos=None, finalising=False):
  """ Reorder a task list.

  This function either moves a task to a given position or puts it last
  in the finalized section. A specific position in the finalized section
  cannot be chosen.

  Moving to the last position can be specified with pos=-1.

  Arguments:
  conn -- the connection
  job_key -- the job key
  task_key -- the key of the task to be positioned
  pos -- the position to put it, zero-indexed

  """
  assert pos != None or finalising, 'you must provide either the pos or finalising == True'

  res = None
  tasks = None
  task_id, tasks = get_task_id_and_dict(conn, job_key, task_key)

  task_list = task_dict_to_list(tasks)
  task_id_before = None
  task_id_after = None

  if pos == -1 or finalising:
    if len(task_list) > 0:
      task_id_last = task_list[-1].task_id
    # the last id may be our task we want to move
    if len(task_list) <= 1:
      task_id_last = None
    elif task_id_last == task_id:
      task_id_last = task_list[-2].task_id
    logging.debug('last task id = %(id)s' % {'id':task_id_last})
    res = move_job_task(conn, job_key, task_id, finalising=finalising, beforeId=task_id_last)
    return res

  try:
    if pos > 0:
      task_id_before = task_list[pos-1].task_id
      assert type(task_id_before) is IntType, 'task_id_before is not an int: %r' % task_id_before
  except:
    pass
  try:
    task_id_after = task_list[pos].task_id
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

def _get_id_and_dict(conn, outer_key, inner_key, get_inner_func, inner_key_name):
  inner_id = None
  inner_dict = {}
  try:
    int(inner_key)  # it's the ID, not the title
    inner_dict = get_inner_func(conn, outer_key)
    if inner_key in inner_dict:
      inner_id = inner_key
  except:          # it's the title
    inner_dict = get_inner_func(conn, outer_key, sort_by_title=True)
    if inner_key in inner_dict:
      inner_id = inner_dict[inner_key][0]

  return inner_id, inner_dict


def get_task_id_and_dict(conn, job_key, task_key):
  """ Get the task id from a task key and a dict with all tasks in the job

  The task key can be the id or the title. This function determines this,
  then downloads the appropriate task dict and resolves to the id.

  """
  return _get_id_and_dict(conn, job_key, task_key, get_tasks, 'task')

def get_job_id_and_dict(conn, plan_key, job_key):
  """ Get the job id from a job key and a dict with all jobs in the job

  The job key can be the id or the title. This function determines this,
  then downloads the appropriate job dict and resolves to the id.

  """
  return _get_id_and_dict(conn, plan_key, job_key, get_jobs, 'job')

def delete_task(conn, plan_key, job_title, task_key):
  """ Deletes a task from one job.

  This function determines the job id to the given job_title,
  the finds the task id from the task_key, and tries to delete it.

  """
  job_id, _ = get_job_id_and_dict(conn, plan_key, job_title)
  logging.debug('JOB ID = %(job_id)s' % {'job_id': job_id,})
  task_id, _ = get_task_id_and_dict(conn, job_id, task_key)
  logging.debug('TASK ID = %(task_id)s' % {'task_id': task_id,})

  try:
    int(task_id)
    res = delete_job_task(conn, job_id, task_id)
  except:
    res = {'status':'OK'}

  return res

def insert_task(conn, plan_key, job_title, task_key, task_params, position=None, finalising=False):
  job_id, _ = get_job_id_and_dict(conn, plan_key, job_title)
  logging.debug('JOB ID = %(job_id)s' % {'job_id': job_id,})
  res = add_job_task(conn, job_id, task_key, task_params)
  print_result_debug(res, 'adding', task_key)
  task_id = res['taskResult']['task']['id']
  logging.debug('TASK ID = %(task_id)s' % {'task_id': task_id,})

  if position != None or finalising == True:
    res = move_task_to_position(conn, job_id, task_id, position, finalising)
    print_result_debug(res, 'positioning', task_key)

  return res

