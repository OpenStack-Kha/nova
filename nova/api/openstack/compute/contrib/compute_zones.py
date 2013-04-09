# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mirantis LLC.
# All Rights Reserved.
#

""" Compute zones management extension"""

import webob
import webob.exc

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack import xmlutil
from nova.compute import api as compute_api
from nova import exception
from nova.openstack.common import log as logging


LOG = logging.getLogger(__name__)
authorize = extensions.extension_authorizer('compute', 'compute_zones')
#soft_authorize = extensions.soft_extension_authorizer('compute', 'compute_zones')


class ComputeZoneTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict('compute_zone'), 1)


class ComputeZonesTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('compute_zones')
        elem = xmlutil.make_flat_dict('compute_zone', selector='compute_zones',
                                      subselector='compute_zone')
        root.append(elem)
        return xmlutil.MasterTemplate(root, 1)


class ComputeNodeTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict('compute_node'), 1)


class ComputeNodesTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('compute_nodes')
        elem = xmlutil.make_flat_dict('compute_node', selector='compute_nodes',
                                      subselector='compute_node')
        root.append(elem)
        return xmlutil.MasterTemplate(root, 1)


class ComputeNodeToZoneTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict('compute_node_to_zone'), 1)


class ComputeZoneController(object):

    """ Compute Zones API controller for the OpenStack API """
    def __init__(self):
        self.api = compute_api.ComputeZoneAPI()

    @wsgi.serializers(xml=ComputeZoneTemplate)
    def create(self, req, name):
        """Create new compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        try:
            zone = self.api.create(context, name)
            return {'compute_zone': zone}
        except exception.NovaException as exc:
            #msg = _("Compute zone '%s' already exists.") % name
            raise webob.exc.HTTPInternalServerError(explanation=exc.message)

    def delete(self, req, name):
        """
        Delete compute zone and remove (detach) all compute nodes
        attached to the compute zone
        """
        context = req.environ['nova.context']
        authorize(context)
        try:
            self.api.delete(context, name)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)
        return webob.Response(status_int=202)

    @wsgi.serializers(xml=ComputeZonesTemplate)
    def list(self, req):
        """List all compute zones"""
        context = req.environ['nova.context']
        authorize(context)
        zones = self.api.list(context)
        zone_list = []
        for zone in zones:
            zone_list.append({'compute_zone': {
                'name': zone['name'],
                }})
        return {'compute_zones': zone_list}

    @wsgi.serializers(xml=ComputeNodeToZoneTemplate)
    def add_node(self, req, zone_id, node_id):
        """Add compute node to the compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        try:
            node_to_zone = self.api.add_node(context, zone_id, node_id)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)
        return {'compute_node_to_zone': node_to_zone}

    def remove_node(self, req, zone_id, node_id):
        """Remove (detach) compute node attached to the compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        try:
            self.api.remove_node(context, zone_id, node_id)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)

    @wsgi.serializers(xml=ComputeNodesTemplate)
    def list_nodes(self, req, zone_id):
        """List all nodes in given compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        nodes = self.api.list_nodes(context, zone_id)
        node_list = []
        for node in nodes:
            node_list.append({'compute_node': {
                'zone': node.zone['name'],
                'id': node.node['id'],
                'name': node.node['hypervisor_hostname'],
                }})
        return {'compute_nodes': node_list}

    def has_node(self, context, zone_id, node_id):
        """Checks whether the compute node attached to the compute zone"""
        return self.db.has_node(context, zone_id, node_id)


class ComputeZones(extensions.ExtensionDescriptor):
    """Compute zone support"""

    name = "ComputeZones"
    alias = "os-computezones"
    namespace = "http://docs.openstack.org/compute/ext/computezones/api/v1.1"
    updated = "2013-04-09T00:00:00+00:00"

    def get_resources(self):
        res = extensions.ResourceExtension(
            'os-computezones',
            ComputeZoneController())
        return res
