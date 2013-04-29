from lib.requests import *
from lib.bamboo_commands import *

conn = external_authenticate('http://localhost:6990', 'cookies.txt')
res = add_mod_plan_variable(conn, 'LCGDM-PUPPET', 'automate', 'them')
print res

