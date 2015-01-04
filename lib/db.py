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


from sqlalchemy import Table, MetaData, orm, create_engine

import constants


class Versions(object):
	pass

class Libraries(object):
	pass

libraries_db = create_engine('sqlite:///%s/libraries.sqlite3' %constants.db_path)
versions_db = create_engine('sqlite:///%s/versions.sqlite3' %constants.db_path)
libraries_meta = MetaData(bind=libraries_db, reflect=True)
versions_meta = MetaData(bind=versions_db, reflect=True)
versions = libraries_meta.tables['versions']
libraries = versions_meta.tables['libraries']
orm.Mapper(Table, versions)
orm.Mapper(Table, libraries)
session = orm.Session(bind = db)

