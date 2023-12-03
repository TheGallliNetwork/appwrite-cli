#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
# use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin('python.pycharm')


name = "appw"
summary = "An alternative CLI wrapper on top of Appwrite API with support " \
          "for creating & restoring snapshots to easily reproduce dev. " \
          "environments."
default_task = "publish"
version = "0.0.2.dev0"
author = "The Gallli Network"
author_email = "support@gallistats.com"
license = "MIT"
url = "https://github.com/TheGallliNetwork/appwrite-cli"


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

    project.set_property("distutils_commands", ['sdist', 'bdist_wheel'])
    project.set_property('distutils_upload_repository_key', 'pypi')
    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_readme_file_type", 'text/markdown')
    project.set_property('distutils_readme_file', 'README.md')
    project.set_property('distutils_description_overwrite', True)
