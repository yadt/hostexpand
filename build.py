from pythonbuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.coverage")
use_plugin("python.pychecker")
use_plugin("python.pymetrics")
use_plugin("python.pylint")
use_plugin("python.distutils")
use_plugin("python.pydev")

use_plugin("copy_resources")
use_plugin("filter_resources")

default_task = ["analyze", "publish"]

version = "1.0.1"
summary = "A tool to expand hostnames based on a pattern language and DNS resolution"
authors = [
    Author("Arne Hilmann", "arne.hilmann@gmail.com"),
    Author("Alexander Metzner", "alexander.metzner@gmail.com"),
    Author("Udo Juettner", "udo.juettner@gmail.com")
]

url = "http://code.google.com/p/yadt"
license = "GNU GPL v3"

@init
def set_properties (project):
    project.depends_on("dnspython", "1.9.4")
    
    project.set_property("coverage_break_build", True)

    project.set_property("pychecker_break_build", True)

    project.get_property("distutils_commands").append("bdist_rpm")    

    project.get_property("filter_resources_glob").append("**/hostexpand/__init__.py")

    project.set_property("copy_resources_target", "$dir_dist")
    project.get_property("copy_resources_glob").append("README")
    project.get_property("copy_resources_glob").append("setup.cfg")

    project.set_property('dir_dist_scripts', 'scripts')

    project.get_property("distutils_commands").append("bdist_egg")
    project.set_property("distutils_classifiers", [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: System :: Networking',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration'])

