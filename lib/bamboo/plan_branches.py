from .. import requests
from types import *

def add_plan_branch(conn, plan_id, branch_name, branch_description=None):
  """ Add a branch to a plan.

  This function only creates the branch.
  It must be configured and enabled afterwards.

  The redirectUrl in the result contains the branch ID.

  """
  assert type(branch_name) is StringType, 'branch_name is not type String: %r' % branch_name
  params = {
      "bamboo.successReturnMode": "json",
      "planKey": plan_id,
      "planKeyToClone": plan_id,
      "branchName": branch_name,
      "branchDescription": branch_description,
      "branchVcsFields": None,
      "checkBoxFields": "tmp.createAsEnabled",
      "confirm": "true",
      "creationOption": "MANUAL",
      "decorator": "nothing"
      }

  res = requests.post_ui_return_json(
      conn,
      conn.baseurl+'/chain/admin/createPlanBranch.action',
      params)

  return res

def enable_plan_branch(conn, branch_id):
  params = {
      "enabled": "false",
      "branchName": "testbranch",
      "branchDescription": "mydesc",
      "branchConfiguration.cleanup.disabled": "true",
      "buildKey": branch_id,
      "checkBoxFields": "enabled",
      "checkBoxFields": "branchConfiguration.cleanup.disabled",
      "planKey": branch_id,
      "returnUrl": "",
      "save": "Save",
      }

  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/branch/admin/config/saveChainBranchDetails.action',
      params)

  return res

def mod_plan_branch_details(conn, branch_id, branch_params):
  """ Modify the branch details.

  The parameters must include:
  * branchDescription
  * branchName
  * enabled

  Arguments:
  conn -- the connection
  branch_id -- the unique ID of the branch
  branch_params -- the parameters in a dictionary

  """
  params = {
      "branchConfiguration.cleanup.disabled": "true",
      "buildKey": branch_id,
      "checkBoxFields": "enabled",
      "checkBoxFields": "branchConfiguration.cleanup.disabled",
      "checkBoxFields": "overrideBuildStrategy",
      "checkBoxFields": "repositoryTrigger",
      "checkBoxFields": "custom.triggerrCondition.plansGreen.enabled",
      "planKey": branch_id,
      "returnUrl": "",
      "save": "Save",
      "selectFields": "selectedBuildStrategy",
      }
  params.update(branch_params)

  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/branch/admin/config/saveChainBranchDetails.action',
      params)

  return res

def delete_plan_branch(conn, branch_id):
  params = {
      "buildKey": branch_id,
      "save": "confirm"
      }

  res = requests.post_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/deleteChain!doDelete.action',
      params)

  return res

def get_plan_branches(conn, plan_id, sort_by_title=False):
  """ Retrieve information about all branches of this plan.

  TODO: reimplement this to use the rest api.

  """
  params = {
      "buildKey": plan_id
      }
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl+'/chain/admin/config/editChainDetails.action',
      params)

  root = res #.getroot()

  branches = {}
  li_branches = root.findall('.//ul[@class="branches"]/li')
  for li in li_branches:
    key = None
    try:
      key = li.find('./a').attrib['id'].rsplit('_',1)[1]
    except:
      logging.error('no key for branch found.')
    edit_link = li.find('./a').attrib['href']
    title = li.find('./a').text

    if sort_by_title:
      branches[title] = (key, edit_link,)
    else:
      branches[key] = (title, edit_link,)

  return branches
