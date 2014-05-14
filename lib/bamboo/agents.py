import logging
from .. import requests


def get_agents(conn, sort_by_status=False):
  params = {}
  res = requests.get_ui_return_html(
      conn,
      conn.baseurl + '/agent/viewAgents.action',
      params)

  root = res  # .getroot()

  agents = {}

  agent_idle_items = root.find_class('agentIdle')
  agent_building_items = root.find_class('agentBuilding')

  for tr in agent_idle_items + agent_building_items:
    name = tr.find('.//a').text
    status = tr.find('.//img').attrib['alt'].lower()
    if status.startswith('building'):
      status = 'building'

    if sort_by_status:
      s = agents.get(status, [])
      s.append(name)
      agents[status] = s
    else:
      agents[name] = status

  return agents
