import logging
from .. import requests
import re

from collections import OrderedDict

def get_tasks(conn, job_id, sort_by_title=False):
  params = {
      "buildKey": job_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/build/admin/edit/editBuildTasks.action',
      params)

  root = res #.getroot()

  tasks = OrderedDict()

  li_items = root.find_class('item')
  for order_id, li in enumerate(li_items, start=1):
    key = int(li.attrib['data-item-id'])
    edit_link = None
    del_link = None
    title = li.find('.//h3').text
    description = None
    try:
      description = li.find('.//div').text
    except:
      pass
    links = li.findall('.//a')
    for l in links:
      href = l.attrib['href']
      match = re.search('editTask', href)
      if match:
        edit_link = href
      match = re.search('confirmDeleteTask', href)
      if match:
        del_link = href
        req_id = href

    if sort_by_title:
      title_desc = (title, description)
      tasks[title_desc] = (key, (title, description), edit_link, del_link, order_id,)
    else:
      tasks[key] = (title, description, edit_link, del_link, order_id,)

  return tasks

def add_job_task(conn, job_id, task_id, task_params):
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": job_id,
      "checkBoxFields": "taskDisabled",
      "confirm": "true",
      "createTaskKey": task_id,
      "decorator": "nothing",
      "taskId": 0,
      "finalising": "true",
      "userDescription": None
      }
  params.update(task_params)
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/edit/createTask.action',
      params)

  return res

def delete_job_task(conn, job_id, task_id):
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": job_id,
      "confirm": "true",
      "createTaskKey": None,
      "decorator": "nothing",
      "taskId": task_id
      }
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/edit/deleteTask.action',
      params)

  return res

def move_job_task(conn, job_id, task_id, finalising=False, beforeId=None, afterId=None):
  """ Move a task in the runtime order.

  Arguments:
  conn -- the connection object
  job_id -- the id of the job
  task_id -- the id of the task to move
  finalising -- true, if task should be a final task
  beforeId -- id of the task which should be before this task
  afterId -- id of the task which should be after this taks

  """
  params = {
      "planKey": job_id,
      "finalising": "true" if finalising else "false",
      "taskId": task_id
      }
  if beforeId:
    params.update({"beforeId": beforeId})
  if afterId:
    params.update({"afterId": afterId})
  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/build/admin/ajax/moveTask.action',
      params)
  logging.debug(params)

  return res
