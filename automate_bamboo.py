from lib.requests import *
from lib.bamboo_commands import *

conn = authenticate('http://localhost:6990', 'admin', 'admin')
#res = add_mod_plan_variable(conn, 'LCGDM-PUPPET', 'automate', 'them')
#print res
res = add_job_requirement(conn, 'LCGDM-PUPPET-JOB1', 'osmajor', 6)
print res

mock_task_key = "ch.cern.bamboo.mock:MockBuild"
mock_task_params = {
  "mockConfig": "epel-${bamboo.capability.system.osmajor}-x86_64.cfg",
  "mockLocation": " http://svn.cern.ch/guest/lcgdm/extras/build/mock",
  "osMajorVersion": "${bamboo.module.req.osmajor}",
  "packageName": "${bamboo.module.name}",
  "publishRepo": None,
  "specLocation": "dist/${bamboo.module.name}.spec",
  "userDescription": "Java Mock Plugin"
  }

res = add_job_task(conn, 'LCGDM-PUPPET-JOB1', mock_task_key, mock_task_params)
print res
