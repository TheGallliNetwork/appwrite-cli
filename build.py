#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
# use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin('python.pycharm')


name = "appw"
default_task = "publish"


@init
def set_properties(project):
    project.set_property("dir_source_main_python", "src/main")
    project.set_property("dir_source_unittest_python", "src/tests")
    project.set_property("dir_source_main_scripts", "src/scripts")

    project.depends_on_requirements("requirements.txt")

    project.set_property('coverage_threshold_warn', 0)

    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_scripts', True)
    # project.set_property('flake8_max_line_length', 80)
    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_ignore', 'E722,W503')
