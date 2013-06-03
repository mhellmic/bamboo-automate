
cmake_minimum_required (VERSION 2.6)

install(PROGRAMS      __init__.py
                      high_level_functions.py
                      manipulate_bamboo_json.py
                      prettyprint_functions.py
        DESTINATION   ${PYTHON_SITE_PACKAGES}/bamboo_automate/
)

add_subdirectory(bamboo)
