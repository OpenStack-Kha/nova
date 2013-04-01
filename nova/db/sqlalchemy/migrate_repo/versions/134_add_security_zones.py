# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
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

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import MetaData, Integer, String, Table

from nova.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # New table
    compute_zone = Table('compute_zone', meta,
                          Column('created_at', DateTime(timezone=False)),
                          Column('updated_at', DateTime(timezone=False)),
                          Column('deleted_at', DateTime(timezone=False)),
                          Column('deleted', Boolean(create_constraint=True, name=None)),
                          Column('id', Integer(), primary_key=True, nullable=False),
                          Column('name', String(length=255), nullable=False),
                          )
    # New table
    compute_nodes_to_zones = Table('compute_nodes_to_zones', meta,
                           Column('created_at', DateTime(timezone=False)),
                           Column('updated_at', DateTime(timezone=False)),
                           Column('deleted_at', DateTime(timezone=False)),
                           Column('deleted', Boolean(create_constraint=True, name=None)),
                           Column('id', Integer(), primary_key=True, nullable=False),
                           Column('zone_id', Integer(), index=True, nullable=False),
                           Column('node_id', Integer(), index=True, nullable=False),
                           )

    tables = [compute_zone, compute_nodes_to_zones]

    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.exception('Exception while creating table %s.', repr(table))
            raise


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    compute_zone = Table('compute_zone', meta, autoload=True)
    compute_nodes_to_zones = Table('compute_nodes_to_zones', meta, autoload=True)

    tables = [compute_zone, compute_nodes_to_zones]

    for table in tables:
        try:
            table.drop()
        except Exception:
            LOG.exception('Exception while dropping table %s.', repr(table))
            raise


