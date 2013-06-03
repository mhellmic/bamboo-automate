cmake_minimum_required (VERSION 2.6)

install(PROGRAMS      __init__.py
                      authenticate.py
                      branches.py
                      jobs.py
                      permissions.py
                      plans.py
                      requirements.py
                      results.py
                      tasks.py
                      variables.py
        DESTINATION   ${PYTHON_SITE_PACKAGES}/bamboo_automate/bamboo/
)
