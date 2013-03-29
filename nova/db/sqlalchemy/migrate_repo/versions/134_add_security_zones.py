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
    security_zone = Table('security_zone', meta,
                          Column('created_at', DateTime(timezone=False)),
                          Column('updated_at', DateTime(timezone=False)),
                          Column('deleted_at', DateTime(timezone=False)),
                          Column('deleted', Boolean(create_constraint=True, name=None)),
                          Column('id', Integer(), primary_key=True, nullable=False),
                          Column('name', String(length=255), unique=True, nullable=False),
                          )
    # New table
    security_zones = Table('security_zones', meta,
                           Column('created_at', DateTime(timezone=False)),
                           Column('updated_at', DateTime(timezone=False)),
                           Column('deleted_at', DateTime(timezone=False)),
                           Column('deleted', Boolean(create_constraint=True, name=None)),
                           Column('id', Integer(), primary_key=True, nullable=False),
                           Column('zone_id', Integer(), index=True, unique=False, nullable=False),
                           Column('host', String(length=255), unique=True, nullable=False),
                           )

    tables = [security_zone, security_zones]

    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.exception('Exception while creating table %s.', repr(table))
            raise


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    security_zone = Table('security_zone', meta, autoload=True)
    security_zones = Table('security_zones', meta, autoload=True)

    tables = [security_zone, security_zones]

    for table in tables:
        try:
            table.drop()
        except Exception:
            LOG.exception('Exception while dropping table %s.', repr(table))
            raise


