# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Boris Pavlovic (boris@pavlovic.me).
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
#    under the License.


from sqlalchemy import MetaData, Integer, String, Table, Column, ForeignKey, DateTime, Boolean, UniqueConstraint

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    compute_node = Table('compute_nodes', meta, autoload=True)
    compute_zone = Table('compute_zones',
                     meta,
                     Column('created_at', DateTime),
                     Column('updated_at', DateTime),
                     Column('deleted_at', DateTime),
                     Column('deleted', Boolean),
                     Column('id', Integer, primary_key=True),
                     Column('name', String(128), unique=True))

    compute_node_compute_zone_association = Table('compute_node_compute_zone_association',
                                              meta,
                                              Column('created_at', DateTime),
                                              Column('updated_at', DateTime),
                                              Column('deleted_at', DateTime),
                                              Column('deleted', Boolean),
                                              Column('id', Integer, primary_key=True),
                                              Column('compute_node_id', Integer, ForeignKey('compute_nodes.id')),
                                              Column('compute_zone_id', Integer, ForeignKey('compute_zones.id')),
                                              UniqueConstraint('compute_node_id', 'compute_zone_id',
                                                               name='_zone_association_uc'))


    compute_zone.create()
    compute_node_compute_zone_association.create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    compute_node = Table('compute_nodes', meta, autoload=True)
    compute_zone = Table('compute_zones', meta, autoload=True)
    compute_node_compute_zone_association = Table('compute_node_compute_zone_association', meta, autoload=True)
    compute_node_compute_zone_association.drop()
    compute_zone.drop()




