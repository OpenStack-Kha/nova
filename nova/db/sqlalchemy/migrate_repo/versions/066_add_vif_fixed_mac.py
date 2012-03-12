# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.from sqlalchemy import *

from sqlalchemy import Column, MetaData, Table, String


meta = MetaData()

new_column = Column('fixed_mac', String(17))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    table = Table('virtual_interfaces', meta, autoload=True)
    table.create_column(new_column)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    table = Table('virtual_interfaces', meta, autoload=True)
    table.c.mac_address.drop()
