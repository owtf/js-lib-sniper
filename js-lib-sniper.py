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
import json
import re
import requests
import json
import operator
import sqlite3

from lib import constants
from lib.logger import Output
from lib.detect import Detect


_VERSION = constants.version
_EMAIL = constants.email
_GUN_ART = constants.gun_art


def is_valid_file(parser, arg, folder = False, bool_return = False):
    """Check if arg is a valid file/folder that already exists on the file system."""
    if folder:
        arg_type = 'folder'
    else:
        arg_type = 'file'
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        if bool_return:
            return False
        parser.error("The %s %s does not exist!" %(arg_type, arg) )
    else:
        if not (os.path.isdir(arg) and folder) and not (os.path.isfile(arg) and not folder):
            if bool_return:
                return False
            parser.error("%s is not a %s!" %(arg, arg_type) )
        if bool_return:
            return True
        return arg


def get_js_from_dir(directory, ignore_js_files):
    """Get javascript files from directory."""
    files = os.listdir(directory)
    js_list = []
    for f in files:
        f = os.path.join(directory, f)
        if f in ignore_js_files:
            continue
        if os.path.isfile(f) and f[-3:] == '.js':
            js_list.append(f)
    return js_list


def library_detect(file):
    d = Detect(file)
    sim_match = d.hash_detect()
    if len(sim_match) == 0:
        return None
    if len(sim_match) == 1:
        return d.extended_info(sim_match[0], detect_method = 'md5 hash matching') 
    parse_match = d.string_parse(sim_match)
    if len(parse_match) == 1:
        return d.extended_info(parse_match[0], detect_method = 'simhash matching')
    version = d.sandbox_execute(parse_match)
    if version:
        return d.extended_info(parse_match[0], detect_method = 'sandbox execution', version = version)
    else:
        return None


def lastversion_online(name):
    base_url = 'http://api.jsdelivr.com/v1/{cdn}/libraries?name={name}&fields=lastversion'
    name = name.replace('.', '')
    cdns = ('jsdelivr', 'google', 'cdnjs')
    lastversion = dict()
    for cdn in cdns:
        url = base_url.replace('{cdn}', cdn)
        url = url.replace('{name}', name)
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError, requests.exceptions.TimeoutException:
            continue
        source = r.text
        try: 
            s = json.loads(source)
        except ValueError:
            continue
        try:
            s = s[0]
        except IndexError:
            continue
        lv = s['lastversion']
        if lv in lastversion.keys():
            lastversion[lv] += 1
        else:
            lastversion[lv] = 1
    lastversion = sorted(lastversion.items(), key=operator.itemgetter(1))
    if lastversion not in (None, []):
        lastversion_found = lastversion[0][0]
    else:
        lastversion_found = None
    return lastversion_found


def update_db(db, row, **kwargs):
    conn = sqlite3.connect(constants.db_path + "/%s.sqlite" %db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if db == 'libraries':
        command = """update %s set {set} where name = '%s';""" %(db, row['parent_name'])
    elif db == 'versions':
        command = """update %s set {set} where name = '%s', version = '%s';""" %(db, row['name'], row['version'])
    for i in kwargs.keys():
        s = str(i) + "=" + "'" + str(kwargs[i]) + "'" + ","
    s = s[:-1]
    command = command.replace('{set}', s)
    print command
    c.execute(command)   
    conn.commit()


def main():
    usage = "%(prog)s [Options] {Target FILE}"
    parser = argparse.ArgumentParser(description = "%s Detect old javascript libraries with vulnerabilities."%(_GUN_ART), 
        epilog="Report bugs to %s."%_EMAIL, usage = usage)
    file_group = parser.add_mutually_exclusive_group(required = True)
    file_group.add_argument('file', help = "javascript library", nargs='?', action = 'store', 
        type = lambda x: is_valid_file(parser, x), metavar = "FILE")
    parser.add_argument('-V', '--version', help = "display the version and exit.", action = 'version', 
        version='%(prog)s '+ _VERSION )
    parser.add_argument('-v', '--verbose', help = "show extended output", 
        action = 'store_true', required = False)
    parser.add_argument('-q', '--quite', help = "dont display to standard output.", 
        action = 'store_true', required = False)
    parser.add_argument('-y', '--yes', help = "assume Yes to all queries and do not prompt.", 
        action = 'store_true', required = False)
    parser.add_argument('-oN', help = "output in normal format respectively, to the given filename.", 
        action = 'store', required = False, metavar = "<file>", dest = 'output_file_normal')
    parser.add_argument('-oX', help = "output logs in XML format respectively, to the given filename.", 
        action = 'store', required = False, metavar = "<file>", dest = 'output_file_xml')
    parser.add_argument('--log', help = "output logs(errors, warnings) to the given filename.", 
        action = 'store', required = False, metavar = "<file>", dest = 'log_file')
    file_group.add_argument('--jsdir', help = "folder to scan for javascript files", action = 'store', 
        type = lambda x: is_valid_file(parser, x, folder = True), metavar = "<folder>")
    file_group.add_argument('--files-from', help = "read the filenames(comma delimited) to be examined from file", 
        action = 'store', required = False, type = lambda x: is_valid_file(parser, x), dest = 'files_from', metavar = "<file>")
    parser.add_argument('--ignore', help = "comma delimited list of paths to ignore", 
        action = 'store', required = False, type = lambda x: is_valid_file(parser, x), dest = 'ignore', metavar = "<paths>")  
    parser.add_argument('--ignore-from', help = "read the paths(comma delimited) to be ignored from file", 
        action = 'store', required = False, type = lambda x: is_valid_file(parser, x), dest = 'ignore_from', metavar = "<file>")        
    parser.add_argument('--proxy', help = "proxy url (http://some.sever:8080)", action = 'store', 
        required = False, dest = 'proxy', metavar = "<url>")
    if len(sys.argv) < 2:
        parser.print_usage()
        parser.exit(0)
    args = parser.parse_args()
    if args.log_file:
        log_file = os.path.abspath(args.log_file)
    else:
        log_file = None
    if args.output_file_normal:
        output_file_normal = os.path.abspath(args.output_file_normal)
    else:
        output_file_normal = None
    if args.output_file_xml:
        output_file_xml = os.path.abspath(args.output_file_xml)
    else:
        output_file_xml = None
    out = Output(stdout = (not args.quite), log_file = log_file, verbose = args.verbose)
    ignore_js_files = []
    if args.ignore:
        ignore_js_files = args.ignore.split(',')
    if args.ignore_from:
        f = open(args.ignore_from, 'r')
        ignore_js_files = f.read()
        f.close()
        ignore_js_files = re.findall(r'[^,(\r\n)\s]+', ignore_js_files)
    if args.jsdir:     
        js_files = get_js_from_dir(args.jsdir, ignore_js_files = ignore_js_files)
        if js_files in (None, []):
            out.warning("No .js file found in folder %s"%args.jsdir)
            out("Exiting.", verbose_text = True)
            sys.exit(0)
        else:
            out("No. of valid .js files: %s" %len(js_files))
    elif args.files_from:
        f = open(args.files_from, 'r')
        js_files = f.read()
        js_files = re.findall(r'[^,(\r\n)\s]+', js_files)
        f.close()
        valid_js_files = []
        invalid_js_files = []
        for js_file in js_files:
            if js_file in ('', None):
                continue
            js_file = os.path.abspath(js_file)
            if js_file in ignore_js_files:
                continue
            if is_valid_file(parser, js_file, bool_return = True):
                valid_js_files.append(js_file)
            else:
                invalid_js_files.append(js_file)
        out("""Read filenames from %s\nTotal Found: %s\nValid .js files: %s""" %(args.files_from, len(js_files), len(valid_js_files)) )
        if len(invalid_js_files) > 0:
            out.warning("Invalid Files: %s"%(len(invalid_js_files)))
        if len(valid_js_files) == 0:
            out("Exiting.", verbose_text = True)
            sys.exit(0)
        cont = 'y'
        if not args.yes:
            cont = raw_input("Continue?[y]: ")
        if cont.lower() in ('y', ''):
            out("'y' not selected. Exiting.", verbose_text = True)
            sys.exit(0)
        js_files = valid_js_files

    if args.file:
            js_files = (args.file, )
    ignore_online_latest_search_list = list()
    for index, js_file in enumerate(js_files):
        out( "%s.) %s"%(index + 1, js_file) )
        detect_result = library_detect(js_file)
        if detect_result == None:
            out( "Unknown Javascript Library!" )
        else:
            out( "Detected using %s method:"%detect_result['detect_method'] , verbose_text = True)
            out( "Name: %s" %detect_result['name'] )
            out( "Version: %s" %detect_result['version'] )
            out( "Parent Name: %s" %detect_result['parent_name'] )
            out( "Author: %s" %detect_result['author'] )
            out( "Description: %s" %detect_result['description'] )
            out( "Homepage: %s" %detect_result['homepage'] )
            check_online = 'y'
            if detect_result['parent_name'] not in ignore_online_latest_search_list:    
                if not args.yes:
                    check_online = raw_input("Check for latest version online?[y]:")
            else:
                check_online = 'n'
            if check_online.lower() not in ('y', ''):
                out("Skipping online check for latest version. Reading data from local db.", verbose_text = True)
                latest_version = detect_result['lastversion']
                ignore_online_latest_search_list.append(detect_result['parent_name'])
            else:
                out( "Checking for lastest version online.." , verbose_text = True)
                ignore_online_latest_search_list.append(detect_result['parent_name'])
                latest_version_online = lastversion_online(detect_result['parent_name'])
                if latest_version_online == None:
                    latest_version = detect_result['lastversion']
                    out.warning( "Connectivity Error", verbose_text = True )
                    out( "Unable to get lastest version online. Reading data from local db." )
                else:
                    latest_version = latest_version_online
                    if latest_version != detect_result['lastversion']:
                        update_db(db = 'libraries', row = detect_result, lastversion = latest_version)
                        out("New version %s found.\nLocal DB updated." %(latest_version), verbose_text = True)
            if detect_result['version'].lower() != latest_version.lower():
                out("")
                out.warning( "This is an old version.\nLatest version available: %s" %latest_version, bold = True)
            else:
                out( "Running latest version." )
        out( "+" * 30)
                



if __name__ == '__main__':
    sys.exit(main())
