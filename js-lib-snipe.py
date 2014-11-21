#!/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import sys
import os


def is_valid_file(parser, arg):
    """Check if arg is a valid file that already exists on the file system."""
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def main():
	parser = argparse.ArgumentParser(description = "Javascript library Sniper description")
	parser.add_argument('-f', '--file', help = "Input Javascript file(s)", action = 'store',
	 required = False, type = lambda x: is_valid_file(parser, x), dest = 'file', metavar = "JS_FILE")
	parser.add_argument('-l', '--list', help = "Input file containing list of(paths) Javascript files",
	 action = 'store', required = False, type = lambda x: is_valid_file(parser, x), dest = 'list_file', metavar = "TXT_FILE")
	#parser.add_argument('')
	if len(sys.argv) < 2:
		parser.print_help()

	args = parser.parse_args()







if __name__ == '__main__':
    sys.exit(main())
