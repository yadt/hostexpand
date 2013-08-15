hostexpand(1) -- expand hostnames based on a pattern language and DNS resolution
================================================================================

## SYNOPSIS

`hostexpand` [options] _host-expression_ [...]

## DESCRIPTION

Expand the host-expressionn into new-line separated list hostnames. Check each host in DNS and return only hosts that can be resolved. Short hostnames can be expanded to FQDNs according to the DNS search path in the local DNS resolver.

## OPTIONS

 * **--version**:
   Show version

 * **--nrformat**=NRFORMAT:
   Set number format, default is `%02i`

 * **--outputformat**=OUTPUTFORMAT:
   Set the output format. Can be one of `shortname`, `fqdn`, or `ip`. Default is `shortname`.

## SYNTAX

The following host-expressions are recognized, different pattern styles can be mixed freely:

 * **Patterns**:
   Expressions like `foo*` are searched in DNS, starting from 1 and going up till no more hosts are found.
   The NRFORMAT sets the length of the number. In this example `foo01`, `foo02` ... would be searched.

 * **Number Ranges**:
   Expressions like `foo[5..10]` are expanded to `foo05`, `foo06`, `foo07`, `foo07`, `foo09`, `foo10`.
   Expressions like `foo[5:10]` are expanded to `foo05`, `foo06`, `foo07`, `foo07`, `foo09`.

 * **Alternatives**:
   Expressions like `{foo|bar}` are expanded to `foo`, `bar`.

 * **File Includes**:
   Expressions including a `/` are interpreted as a file to read, the file should contain hostnames one per line. # comments and empty lines are ignored.

## SEE ALSO
 * Build status: [![Build Status](https://secure.travis-ci.org/yadt/hostexpand.png)](http://travis-ci.org/yadt/hostexpand)
 * Homepage: http://github.com/yadt/hostexpand

## Installation with pip
It is considered good practice to install all packages available via pip & easy_install in a
[virtual environment](http://pypi.python.org/pypi/virtualenv) so that your development dependencies are isolated from the system-wide dependencies.

  1. create a virtual environment for building

     `virtualenv ve`
  1. activate the virtual environment

     `source ve/bin/activate`
  1. install the hostexpand from PyPi

     `pip install hostexpand`

## LICENSE

Licensed under the GNU General Public License (GPL), see http://www.gnu.org/licenses/gpl.txt for full license text.

