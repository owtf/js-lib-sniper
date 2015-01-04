#!../virtualenv_python/bin/python
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
import os
import hashlib
import operator
import difflib
import re
import json

from simhash import Simhash
from jsmin import jsmin
import sqlite3

import constants

from lib import sandbox

#from db import session, db


def strip_js_suffix(name):
    """Remove the .js/.min.js suffix from the filename"""
    if name[-8:] in ('.min.js, -min.js, _min.js'):
        name = name[:-8]
    elif name[-3:] == '.js':
        name = name[:-3]
    return name

class Detect(object):
    """Detect library name and version."""
    def __init__(self, filepath):
        self.filepath = filepath
        f = open(filepath, 'r')
        self.library_text = f.read()
        f.close()
        self.basename = os.path.basename(filepath)

    def hash_detect(self, max_returns = 20):
        """Compare the simhash/md5hash value with pre-computed hashes."""
        #pass
        library_text_min = jsmin(self.library_text)
        md5_hash = hashlib.md5(library_text_min.encode('utf-8')).hexdigest()
        """
        md5_match = session.query(Versions).filter(Versions.md5_hash == md5_hash).first()
        if md5_match not in (None, [], '', {}):
            pass
            #found
        """

        conn = sqlite3.connect(constants.db_path + "/versions.sqlite")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""select * from versions where md5_hash = '%s';"""%md5_hash)
        md5_match = c.fetchall()
        if md5_match not in (None, [], '', {}):
            #print md5_match
            return (md5_match)
        sim_hash = Simhash(library_text_min).value
        #print "SELECT *, (ABS( (SELECT substring(simhash,1,11)) -(SELECT substring('%s',1,11)) )*100000000 + ABS( (SELECT substring(simhash FROM 12)) -(SELECT substring('%s' FROM 12))) ) AS diff FROM versions ORDER BY diff ASC LIMIT %s;" %(sim_hash, sim_hash, max_returns)
        sim_match = c.execute("""SELECT *, (ABS( (SELECT substr(simhash,1,11)) -
         (SELECT substr('%s',1,11)) )*100000000 + ABS( (SELECT substr(simhash, 12)) -
          (SELECT substr('%s',12))) ) AS diff FROM versions ORDER BY diff ASC LIMIT %s;""" %(sim_hash, sim_hash, max_returns) ).fetchall()
        previous_diff = 1
        for index, i in enumerate(sim_match):
            try:
                if i['diff'] / previous_diff > 3  and index != 0:
                    break
            except ZeroDivisionError:
                pass
            previous_diff = i['diff']

        sim_match = sim_match[:index]
        self.sim_match = sim_match
        return sim_match

    def string_parse(self, libraries = None):
        """Extract library name, version from filename/ source text."""
        if libraries == None:
            libraries = self.sim_match
        file_prefix = strip_js_suffix(self.basename)
        filename_list = []
        lowest_diff = 100000000;
        library_parent_name_list = dict()
        for index, i in enumerate(libraries):
            if i['parent_name'] in library_parent_name_list.keys():
                library_parent_name_list[i['parent_name']]['score'] += 1
                library_parent_name_list[i['parent_name']]['indexes'].append(index)
            else:

                library_parent_name_list[i['parent_name']] = {'score':0, 'indexes':[index]}
            diff = difflib.SequenceMatcher(None, i['name'].lower(), file_prefix.lower()).ratio()
            if diff < lowest_diff:
                lowest_diff = diff
                prefix_match = i

        library_parent_name_list = sorted(library_parent_name_list.items(), key=operator.itemgetter(1))

        if library_parent_name_list[0][0] == prefix_match['parent_name']:
            library_group = prefix_match
        else:
            library_group = libraries[library_parent_name_list[0][1]['indexes'][0]]
        #comments search for version
        parent_name = library_group['parent_name']
        #versions = session.query(Libraries.versions).filter(Libraries.name == parent_name).first()
        #conn = sqlite3.connect(constants.db_path + "/libraries.sqlite")
        conn = sqlite3.connect(constants.db_path + "/versions.sqlite")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        #versions = c.execute("select versions from libraries where name = '%s';" %parent_name).fetchone()
        #versions = versions[0]
        #versions = eval(versions)
        versions = c.execute("select version from versions where parent_name = '%s';" %parent_name).fetchall()
        v_list = dict()
        #print versions
        for version in versions:
            version = version[0]
            version_text = re.findall(r"(^.*?%s.*?$)" %version, self.library_text, re.MULTILINE)
            #print version_text
            if version_text:
                for v in version_text:
                    #print v
                    if strip_js_suffix( library_group['parent_name']).lower() in v.lower() or strip_js_suffix(library_group['name']).lower()  in v.lower():
                        v_list[version] = 1 if version not in v_list.keys() else v_list[version] + 1
                        #break


        max_score = max(v_list.values()) if v_list.values() else None
        version_found = [k for k,v in v_list.items() if v == max_score]
        version_found = list(set(version_found))

        #print version_found
        if version_found not in ([], None):
            lib_found = None
            try:
                for index in library_parent_name_list[0][1]['indexes']:
                        #print library_parent_name_list[0]
                        #for lib in libraries[index]:
                        lib = libraries[index]
                        #print libraries[index]
                        #print version_found, lib['version']
                        for v in version_found:
                            if lib['version'] == v:
                                lib_found = lib
                                raise StopIteration;
            except StopIteration: 
                pass
            if lib_found:
                return (lib_found,)
        lib_list = list()
        for index in library_parent_name_list[0][1]['indexes']:
            lib_list.append(libraries[index])
        return lib_list

    def sandbox_execute(self, parse_match):
        """Execute the javascript library inside webkit browser"""
        s = sandbox.Sandbox()
        s.execute(self.library_text)
        ##############################only for jquery[more command to be added.]
        return s.execute('jQuery.fn.jquery;')
        s.close()

    def extended_info(self, library_dict, **kwargs):
        """Return extended information about the library"""
        parent_name = library_dict['parent_name']
        version = library_dict['version']
        conn = sqlite3.connect(constants.db_path + "/libraries.sqlite")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()    
        info = c.execute("""select * from libraries where name = '%s'""" %parent_name).fetchone()
        extended_info = dict()
        extended_info['name'] = library_dict['name']
        extended_info['parent_name'] = info['name']
        extended_info['mainfile'] = info['mainfile']
        extended_info['version'] = library_dict['version']
        extended_info['lastversion'] = info['lastversion']
        extended_info['description'] = info['description']
        extended_info['homepage'] = info['homepage']
        extended_info['author'] = info['author']
        for k in kwargs.keys():
            extended_info[k] = kwargs[k]
        return extended_info

