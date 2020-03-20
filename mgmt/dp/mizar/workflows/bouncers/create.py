import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

dividers_opr = DividerOperator()
droplets_opr = DropletOperator()
bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()
nets_opr = NetOperator()

class BouncerCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		bouncer = bouncers_opr.get_bouncer_stored_obj(self.param.name, self.param.spec)
		while not droplets_opr.is_bootstrapped():
			pass

		droplets_opr.assign_bouncer_droplet(bouncer)

		# Update net on dividers
		net = nets_opr.store.get_net(bouncer.net)
		if net:
			dividers_opr.update_bouncer_with_dividers(bouncer, net) #Fix this (word choice)

		# Update vpc on bouncer
		dividers_opr.update_vpc(bouncer)

		endpoints_opr.update_bouncer_with_endpoints(bouncer)
		endpoints_opr.update_endpoints_with_bouncers(bouncer)

		bouncers_opr.set_bouncer_provisioned(bouncer)
		self.finalize()