 # Bamboo Automation

 This set of tools should allow to automate some of the task you want to do on Bamboo.
 It uses the rest api whenever possible and the web ui otherwise.

 ## Install

 * Checkout the source from git

 ## Structure

 ```lib/requests.py
 lib/bamboo_commands.py
 ```

 * **lib/requests.py** handles the http requests
 * **lib/bamboo_commands.py** provides bamboo actions like add_job_requirement()
 * **main dir** holds example files. that will work on a local dev bamboo

 ## Bugs/Todo

 * the external authentication using a cookies file does not work
