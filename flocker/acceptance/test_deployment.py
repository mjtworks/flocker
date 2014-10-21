# Copyright Hybrid Logic Ltd.  See LICENSE file for details.

"""
Tests for deploying applications.
"""
from twisted.internet.defer import gatherResults

from twisted.trial.unittest import TestCase

from flocker.node._docker import BASE_NAMESPACE, Unit

from .utils import (flocker_deploy, get_nodes, RemoteDockerClient,
                    require_flocker_cli, assertExpectedDeployment)


class DeploymentTests(TestCase):
    """
    Tests for deploying applications.

    Similar to:
    http://doc-dev.clusterhq.com/gettingstarted/tutorial/
    moving-applications.html#starting-an-application
    """
    @require_flocker_cli
    def test_deploy(self):
        """
        Deploying an application to one node and not another puts the
        application where expected. Where applicable, Docker has internal
        representations of the data given by the configuration files supplied
        to flocker-deploy.
        """
        d = get_nodes(num_nodes=2)

        def deploy(node_ips):
            node_1, node_2 = node_ips

            application = u"mongodb-example"
            image = u"clusterhq/mongodb"

            minimal_deployment = {
                u"version": 1,
                u"nodes": {
                    node_1: [application],
                    node_2: [],
                },
            }

            minimal_application = {
                u"version": 1,
                u"applications": {
                    application: {
                        u"image": image,
                    },
                },
            }

            flocker_deploy(self, minimal_deployment, minimal_application)

            # TODO github.com/ClusterHQ/flocker/pull/897#discussion_r19024229
            # This assertion setup code is very similar to the one in previous
            # test; probably we can make utility assertion function that
            # covers both cases.
            # TODO this has some defaults in it
            unit = Unit(name=application,
                        container_name=BASE_NAMESPACE + application,
                        activation_state=u'active',
                        container_image=image + u':latest',
                        ports=frozenset(), environment=None, volumes=())

            d = assertExpectedDeployment({
                node1: set([unit]),
                node_2: set([]),
            })

            return d

        d.addCallback(deploy)
        return d
