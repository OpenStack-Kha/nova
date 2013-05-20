from webob import exc

from nova.api.openstack import extensions
from nova import db
from nova import context
from nova.api.openstack import wsgi
from nova.api.openstack import common
from nova import exception
from nova.openstack.common import log as logging


class ZonesViewBuilder(common.ViewBuilder):

    _collection_name = "zones"

    def zone_view(self, zone):
        """Return a dictionary with basic image attributes."""
        return {
            "zone": {
                "id": zone.__dict__['Zone ID'],
                "name": zone.__dict__['Zone name'],
            },
        }

    def association_view(self, zone):
        """Return a dictionary with basic image attributes."""
        return {
            "zone": {
                "zone_name": zone.__dict__['Zone name'],
                "node_id": zone.__dict__['Node ID'],
            },
        }

    def list_zones(self, zones):
        """Construct zone list"""
        zone_list = [self.zone_view(zone)["zone"] for zone in zones]
        return dict(zones=zone_list)

    def list_associations(self, zones):
        """Construct zone list"""
        zone_list = [self.association_view(zone)["zone"] for zone in zones]
        return dict(zones=zone_list)

    def _print_list(self, zone_list):
        labels = []
        print '-'*48
        for zone_record in zone_list:
            #print header
            if labels is not zone_record.__dict__['_labels']:
                labels = zone_record.__dict__['_labels']
                print '|', '|'.join('  %-8s' % v for v in labels), '|'
            print '|', '|'.join('  %-8s' % zone_record.__dict__[v] for v in labels), '|'

        print '-'*48


    @staticmethod
    def _format_date(date_string):
        """Return standard format for given date."""
        if date_string is not None:
            return date_string.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def _get_status(image):
        """Update the status field to standardize format."""
        return {
            'active': 'ACTIVE',
            'queued': 'SAVING',
            'saving': 'SAVING',
            'deleted': 'DELETED',
            'pending_delete': 'DELETED',
            'killed': 'ERROR',
        }.get(image.get("status"), 'UNKNOWN')

    @staticmethod
    def _get_progress(image):
        return {
            "queued": 25,
            "saving": 50,
            "active": 100,
        }.get(image.get("status"), 0)


class ZoneController(wsgi.Controller):
    """Zone API"""

    _view_builder_class = ZonesViewBuilder()

    def __init__(self):
        pass

    def list(self, req):

        zone_name = None

        if 'zone_name' in req.GET:
            zone_name = req.GET['zone_name']

        try:
            zone_list = db.compute_zone_list(context.get_admin_context(), zone_name)

            if zone_name:
                response = self._view_builder_class.list_associations(zone_list)
            else:
                response = self._view_builder_class.list_zones(zone_list)

        except exception.DBError as ex:
            new_ex = exception.Invalid()
            new_ex.message = ex.inner_exception.message
            raise new_ex

        return response

    def add(self, req):

        zone_name = None
        node_id = None

        if 'zone_name' in req.GET:
            zone_name = req.GET['zone_name']

        if 'node_id' in req.GET:
            node_id = req.GET['node_id']

        try:
            zone_list = db.compute_zone_add(context.get_admin_context(), zone_name, node_id)

            if node_id:
                response = self._view_builder_class.list_associations(zone_list)
            else:
                response = self._view_builder_class.list_zones(zone_list)

        except exception.DBError as ex:
            new_ex = exception.Invalid()
            new_ex.message = ex.inner_exception.message
            raise new_ex

        return response

    def delete(self, req):
        zone_name = None
        node_id = None

        if 'zone_name' in req.GET:
            zone_name = req.GET['zone_name']

        if 'node_id' in req.GET:
            node_id = req.GET['node_id']

        try:
            db.compute_zone_delete(context.get_admin_context(), zone_name, node_id)
            zone_list = db.compute_zone_list(context.get_admin_context(), zone_name)

            if node_id:
                response = self._view_builder_class.list_associations(zone_list)
            else:
                response = self._view_builder_class.list_zones(zone_list)

        except exception.DBError as ex:
            new_ex = exception.Invalid()
            new_ex.message = ex.inner_exception.message
            raise new_ex

        return response


def create_resource():
    return wsgi.Resource(ZoneController())
