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


import logging


class Output(object):
    """Output to logfile and stdout."""
    def __init__(self, stdout = True, log_file = False, verbose = False):
        self.stdout = stdout
        self.log_file = log_file
        self.verbose = verbose
        if log_file:
            logging.basicConfig(filename = log_file, level=logging.INFO, 
                format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            self.logger = logging.getLogger('')

    def __call__(self, text, verbose_text = False):
            self.normal(text, verbose_text)

    def normal(self, text, verbose_text = False):
        if self.log_file:
            logging.info(text)
        if self.stdout and ( not verbose_text or (verbose_text and self.verbose)):
            print text

    def debug(self, text, verbose_text = False):
        if self.log_file:
            logging.debug(text)
        if self.stdout and ( not verbose_text or (verbose_text and self.verbose)):
            print "Debug: " + text  

    def warning(self, text, verbose_text = False, bold = False):
        if self.log_file:
            logging.warn(text)
        if self.stdout and ( not verbose_text or (verbose_text and self.verbose)):
            if not bold:
                print "Warning: " + text
            else:
                print "WARNING: " + text

    def error(self, text, verbose_text = False):
        if self.log_file:
            logging.error(text)
        if self.stdout and ( not verbose_text or (verbose_text and self.verbose)):
            print "Error: " + text     

    def critical(self, text, verbose_text = False):
        if self.log_file:
            logging.critical(text)
        if self.stdout and ( not verbose_text or (verbose_text and self.verbose)):
            print "Critical: " + text     
       