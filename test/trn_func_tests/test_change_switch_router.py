# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.controller import controller
from test.trn_controller.droplet import droplet
from test.trn_controller.common import cidr
from test.trn_func_tests.helper import *
import unittest
from time import sleep


class test_change_switch_router(unittest.TestCase):

    def setUp(self):
        # Testing the following multiple subnetwork scenario, while
        # adding switchs and routers during connection
        # +------------+      +------------+        +------------+      +------------+
        # |     D1     |      |     D2     |        |     D3     |      |     D4     |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | |  ns1   | |      | |  ns2   | |        | |  ns3   | |      | |  ns4   | |
        # | |        | |      | |        | |        | |        | |      | |        | |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | | veth0  | |      | | veth0  | |        | | veth0  | |      | | veth0  | |
        # | |10.0.0.1| |      | |10.0.0.2| |        | |20.0.0.1| |      | |20.0.0.2| |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | |Transit | |      | |Transit | |        | |Transit | |      | |Transit | |
        # | | Agent  | |      | | Agent  | |        | | Agent  | |      | | Agent  | |
        # | | peer1  | |      | | peer2  | |        | | peer3  | |      | | peer4  | |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # +------------+      +------------+        +------------+      +------------+
        # |Transit XDP |      |Transit XDP |        |Transit XDP |      |Transit XDP |
        # |    eth0    |      |    eth0    |        |    eth0    |      |    eth0    |
        # +------------+      +------------+        +------------+      +------------+
        #       |                   |                     |                   |
        #       |   +------------+  |                     |   +------------+  |
        #       |   |  Switch1   |  |                     |   |  Switch4   |  |
        #       |   |  Switch2   |  |                     |   |  Switch5   |  |
        #       |   |  Switch3   |  |                     |   |  Switch6   |  |
        #       |   |10.0.0.0/16 |  |                     |   |20.0.0.0/16 |  |
        #       |   |            |  |                     |   |            |  |
        #       +---|            |--+                     +---|            |--+
        #           |            |                            |            |
        #           |            |                            |            |
        #           +------------+                            +------------+
        #           |Transit XDP |                            |Transit XDP |
        #           |    eth0    |                            |    eth0    |
        #           +------------+                            +------------+
        #                  |              +------------+             |
        #                  |              |  Router1   |             |
        #                  |              |  Router2   |             |
        #                  |              |  Router3   |             |
        #                  |              |            |             |
        #                  |              |    VPC3    |             |
        #                  +--------------|            |-------------+
        #                                 |            |
        #                                 |            |
        #                                 +------------+
        #                                 |Transit XDP |
        #                                 |    eth0    |
        #                                 +------------+

        # a. Switch 3, Switch6 and Router3 are all hosted on the same
        # host
        # b. Switch 2 is hosted on D3
        # c. Switch 5 is hosted on D2

        self.droplets = {
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "d5": droplet("d5"),
            "switch-1": droplet("switch-1"),
            "switch-4": droplet("switch-4"),
            "router-1": droplet("router-1"),
            "router-2": droplet("router-2"),
        }

        self.c = controller(self.droplets)

        self.c.create_vpc(3, cidr("16", "10.0.0.0"), ["router-1"])

        self.c.create_network(3, 10, cidr("24", "10.0.0.0"), ["switch-1"])

        self.c.create_network(3, 20, cidr("24", "10.20.0.0"), ["switch-4"])

        self.ep1 = self.c.create_simple_endpoint(3, 10, "10.0.0.2", "d1")
        self.ep2 = self.c.create_simple_endpoint(3, 10, "10.0.0.3", "d2")

        self.ep3 = self.c.create_simple_endpoint(3, 20, "10.20.0.4", "d3")
        self.ep4 = self.c.create_simple_endpoint(3, 20, "10.20.0.5", "d4")

    def tearDown(self):
        pass

    def do_scenario_change(self):
        self.c.add_router(3, "router-2")

        self.c.add_switch(3, 10, "d3")
        self.c.add_switch(3, 10, "d5")

        self.c.add_switch(3, 20, "d2")
        self.c.add_switch(3, 20, "d5")

        self.c.add_router(3, "d5")

    def do_scenario_reset(self):
        pass

    def test_change_switch_router(self):
        logger.info(
            "{} Testing a long connection is not impacted by adding switches and routers! {}".format('='*20, '='*20))
        do_long_tcp_test(self, self.ep1, self.ep4)
        do_check_failed_rpcs(self, self.droplets.values())
