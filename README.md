
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
Get the keys from the bamboo json output.
Plan keys include the project key in a projectkey-plankey schema, so you can access the plan with the plan key only.
The keys are unique string representations for a project or plan.

    project_keys = get_project_keys(project_dict)
    plan_keys = get_plan_keys(plan_dict)

### Manipulate Variables
Get the plan key first

    plan_key = 'PROJECTKEY-PLANKEY'

#### Add a Variable
This will fail if the variable already exists

    res = add_plan_variable(conn, plan_key, 'varkey', varvalue')

#### Modify a Variable
This will only work if the variable already exists

    res = mod_plan_variable(conn, plan_key, 'varkey', 'varvalue')

#### Add/Modify a Variable
Tries to add the variable and modifies if it exists

    res = add_mod_plan_variable(conn, plan_key, 'varkey', 'varvalue')

#### Delete Variables
You can delete one variable specified by key or delete all at once

    res = delete_plan_variable(conn, plan_key, 'varkey')
    res = delete_plan_all_variables(conn, plan_key)

### Get Job ID
Get the ID of the plan's jobs.
For jobs the key is the name presented on the website, the id the unique internal string representation.
The result is different from get _ projects() or get _ plans(). It returns a dict of tuples.

    job_key = 'Build'
    job_dict = get_jobs(conn, plan_key)
    job_id = job_dict[job_key][0]

### Manipulate Requirements
Requirements are job-bound, so we need the job ID

    job_id = 'PROJECTKEY-PLANKEY-JOB1'

#### Add a Requirement
This will fail if the requirement already exists.
If you add a requirement that is already in the system, the parameter req _ exists must be True.

    res = add_job_requirement(conn, job_id, 'reqkey', 'reqvalue', req_exists=False)
<!--
#### Modify a Requirement
This will only work if the requirement already exists

    res = mod_job_requirement(conn, job_id, 'reqkey', reqvalue')

#### Add/Modify a Requirement
Tries to add the requirement and modifies if it exists

    res = add_mod_job_requirement(conn, job_id, 'reqkey', reqvalue')
-->
#### Delete Requirements
You can delete one requirement specified by key or delete all at once

    res = delete_job_requirement(conn, job_id, 'reqkey')
    res = delete_job_all_requirements(conn, job_id)

### Manipulating Tasks
Tasks are job-bound, so we need the job ID.
We also need the task key and the task parameters. This example shows the sourcecode checkout task.
Fields that are not needed, like userDescription, can be left empty ("").

    job_id = 'PROJECTKEY-PLANKEY-JOB1'


    task_key = "com.atlassian.bamboo.plugins.vcs:task.vcs.checkout"
    task_params = {
        "checkBoxFields": "cleanCheckout",
        "checkoutDir_0": "<where_to_checkout>",
        "selectFields": "selectedRepository_0",
        "selectedRepository_0": "defaultRepository",
        "userDescription": "<my_task_description>"
        }

#### Add a Task
A task can be added multiple times without problems

    res = add_job_task(conn, job_id, task_key, task_params)

#### Move a Task
In bamboo you can move a task precisely. This function, however, only puts tasks into the final stage or back so far.
This function needs the task id, which can be best retrieved with the task description.

    task_description = "<my_task_description>"
    task_dict = get_tasks(conn, job_id)
    for task_id, (task_key, description, edit_link, del_link) in job_tasks.iteritems():
      if description == task_description:
        res = move_job_task(conn, job_id, task_id, finalising=True)

#### Delete Task
This function needs the task id, which can be best retrieved with the task description.

    task_description = "<my_task_description>"
    task_dict = get_tasks(conn, job_id)
    for task_id, (task_key, description, edit_link, del_link) in job_tasks.iteritems():
      if description == task_description:
        res = delete_job_task(conn, job_id, task_id)

### Change Permissions
You can change a permission by specifying it as a four-tuple: (usertype, username, permissiontype, value).
All other values remain unchanged. This function is not very efficient for multiple changes,
since it requests a permission list from bamboo on every invocation.

* The usertype takes values 'user', 'group' or 'other.
* The username is the short username in bamboo.
* The permissiontype is 'read', 'write', 'build', 'clone', 'admin', or 'all' to change all permissions for this user.
* The value is either True or False.

<b></b>

    change_plan_permission(conn,
                           plan_key,
                           ('user','admin','all',True))
    change_plan_permission(conn,
                           plan_key,
                           ('group','devel','build',True))
    change_plan_permission(conn,
                           plan_key,
                           ('other','Anonymous Users','all',False))

### Common Operations
These are hints how to do common operations on results. They might not be optimal solutions.

#### Delete a Number of Specific Tasks
    tasks_to_delete = [
        'my install task',
        'my build task'
        ]
    for task_id, (task_key, description, _, _) in job_tasks.iteritems():
      if description in tasks_to_delete:
        res = delete_job_task(conn, install_job_id, task_id)

#### Add Multiple Requirements
    requirements = {
      "system.arch": "x86_64",
      "system.osfamily": "RedHat"
      }
    for req_key, req_value in requirements.iteritems():
      res = add_job_requirement(conn, install_job_id, req_key, req_value)

#### How To Get the Task Parameters
Take Firefox with the firebug plugin and open the network tab. Make sure that you have 'persist' set, so connection details stay after page reloads.
Add a task and look at the POST parameters. You don't have to specify all of them, the common ones are set by the function add _ job _ task(). If you're unsure, check the source.

#### Add an Inline Script Task

    scriptBody = """<the whole script content surrounded by three quotes for multiline strings>"""

    cp_task_key = "com.atlassian.bamboo.plugins.scripttask:task.builder.script"
    cp_task_params = {
        "argument": "",
        "environmentVariables": "",
        "script": "",
        "scriptBody": scriptBody,
        "scriptLocation": "INLINE",
        "selectFields": "scriptLocation",
        "userDescription": "<description>",
        "workingSubDirectory": ""
        }

#### Get Plans from one Project

    project = 'MYPROJ'
    print 'PROJECT = %s' % project

    plan_list = get_plans(conn, 'plans.plan.actions')
    plan_keys = get_plan_keys(plan_list)
    print 'PLAN KEYS = %s' % project

    myproj_plan_keys = filter(lambda s: re.match(project,s) != None, plan_keys)
    print 'PLAN KEYS IN PROJECT %s = %s' % (project, myproj_plan_keys)

