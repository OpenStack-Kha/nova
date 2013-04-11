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
authorize = extensions.extension_authorizer('compute', 'computezones')


class ComputeZoneTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict(
            'compute_zone'), 1)


class ComputeZonesTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('compute_zones')
        elem = xmlutil.make_flat_dict('compute_zone',
                                      selector='compute_zones',
                                      subselector='compute_zone')
        root.append(elem)
        return xmlutil.MasterTemplate(root, 1)


class ComputeNodeTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict(
            'compute_node'), 1)


class ComputeNodesTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('compute_nodes')
        elem = xmlutil.make_flat_dict('compute_node',
                                      selector='compute_nodes',
                                      subselector='compute_node')
        root.append(elem)
        return xmlutil.MasterTemplate(root, 1)


class ComputeNodeToZoneTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        return xmlutil.MasterTemplate(xmlutil.make_flat_dict(
            'compute_node_to_zone'), 1)


class ComputeZoneController(object):

    """ Compute Zones API controller for the OpenStack API """
    def __init__(self):
        self.api = compute_api.ComputeZoneAPI()

    @wsgi.serializers(xml=ComputeZoneTemplate)
    def create(self, req, body):
        """Create new compute zone"""
        context = req.environ['nova.context']
        authorize(context)

        params = body['compute_zone']
        name = params['name']
        try:
            zone = self.api.create(context, name)
            return {'compute_zone': zone}
        except exception.NovaException as exc:
            #msg = _("Compute zone '%s' already exists.") % name
            raise webob.exc.HTTPInternalServerError(explanation=exc.message)

    def delete(self, req, id):
        """
        Delete compute zone and remove (detach) all compute nodes
        attached to the compute zone
        """
        context = req.environ['nova.context']
        authorize(context)

        #params = body['compute_zone']
        #name = params['name']
        try:
            self.api.delete(context, id)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)
        return webob.Response(status_int=202)

    @wsgi.serializers(xml=ComputeZonesTemplate)
    def index(self, req):
        """List all compute zones"""
        context = req.environ['nova.context']
        authorize(context)
        zones = self.api.list(context)
        zone_list = []
        for zone in zones:
            zone_list.append({
                'id': zone['id'],
                'name': zone['name'],
                })
        return {'compute_zones': zone_list}

    def action(self, req, id, body):
        _actions = {
            'add_node': self.add_node,
            'remove_node': self.remove_node,
            'list_nodes': self.list_nodes,
            }
        for action, data in body.iteritems():
            try:
                return _actions[action](req, id, data)
            except KeyError:
                msg = _("Aggregates does not have %s action") % action
                raise webob.exc.HTTPBadRequest(explanation=msg)

        raise webob.exc.HTTPBadRequest(explanation=_("Invalid request body"))

    @wsgi.serializers(xml=ComputeNodeToZoneTemplate)
    def add_node(self, req, id, body):
        """Add compute node to the compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        node = body['node']
        try:
            node_to_zone = self.api.add_node(context, id, node)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)
        return {'compute_node_to_zone': node_to_zone}

    @wsgi.serializers(xml=ComputeNodeToZoneTemplate)
    def remove_node(self, req, id, body):
        """Remove (detach) compute node attached to the compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        node = body['node']
        try:
            self.api.remove_node(context, id, node)
        except exception.NovaException as exc:
            raise webob.exc.HTTPInternalServerError(message=exc.message)
        return {'compute_node_to_zone': None}

    @wsgi.serializers(xml=ComputeNodesTemplate)
    def list_nodes(self, req, id, body):
        """List all nodes in given compute zone"""
        context = req.environ['nova.context']
        authorize(context)
        nodes = self.api.list_nodes(context, int(id))
        node_list = []
        for node in nodes:
            node_list.append({
                'zone_name': node.zone['name'],
                'node_id': node.node['id'],
                'node_name': node.node['hypervisor_hostname'],
                })
        return {'compute_nodes': node_list}


class Compute_zones(extensions.ExtensionDescriptor):
    """Compute zone support"""

    name = "ComputeZones"
    alias = "os-computezones"
    namespace = "http://docs.openstack.org/compute/ext/computezones/api/v1.1"
    updated = "2013-04-09T00:00:00+00:00"

    def get_resources(self):
        resources = []
        res = extensions.ResourceExtension(
            'os-computezones',
            ComputeZoneController(),
            member_actions={"action": "POST", })
        resources.append(res)
        return resources
