
# Bamboo Automation

This set of tools should allow to automate some of the task you want to do on Bamboo.
It uses the rest api whenever possible and the web ui otherwise.

## Install

* Checkout the source from git

## Structure

    lib/requests.py
    lib/bamboo_commands.py
    lib/manipulate_bamboo_json.py


* **lib/requests.py** handles the http requests
* **lib/bamboo_commands.py** provides bamboo actions like add_job_requirement()
* **lib/manipulate_bamboo_json.py** retrieve values from the bamboo results
* **main dir** holds example files. that will work on a local dev bamboo, but be notoriously out of date

## Examples
This section lists the usable commands.

They assume that you have imported the libraries like this

    from lib.bamboo_commands import *
    from lib.manipulate_bamboo_json import *

### Create Connection
Either use username and password

    conn = authenticate('http://localhost:6990', 'admin', 'admin', '/bamboo')

or take a JSESSIONID cookie from a file in the Mozilla format

    conn = external_authenticate('http://localhost:6990', 'cookies.txt', '/bamboo')

(there is a firefox extension to export cookies)

The last parameter specifies a directory prefix, where bamboo can be found. If you don't need a prefix, don't specify it or make it empty ('').

### List Projects
Lists all projects

    project_dict = get_projects(conn)

You can use the expand option with the valid parameters from [bamboo's REST API definition] (https://developer.atlassian.com/display/BAMBOODEV/Bamboo+REST+Resources#BambooRESTResources-ProjectService "Bamboo REST API Projects")

    project_dict = get_projects(conn, expand="projects.project.plans)

### List Plans
List all plans

    plan_dict = get_plans(conn)

You can use the expand option with the valid parameters from [bamboo's REST API definition] (https://developer.atlassian.com/display/BAMBOODEV/Bamboo+REST+Resources#BambooRESTResources-PlanService "Bamboo REST API Projects")

    project_dict = get_projects(conn, expand="plans.plan)

### Get Project and Plan Keys
Get the keys from the bamboo json output

    project_keys = get_project_keys(project_dict)
    plan_keys = get_plan_keys(plan_dict)

