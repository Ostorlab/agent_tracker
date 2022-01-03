"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
import multiprocessing
import time
import logging
from urllib import parse
from typing import Dict, Optional, List

import docker

from ostorlab.agent import agent
import utils


logger = logging.getLogger(__name__)
SLEEP_SEC = 3
SCAN_DONE_TIMEOUT_SEC = 10
POSTSCANE_DONE_TIMEOUT_SEC = 10


class TrackerAgent(agent.Agent):
    """Agent responsible for tracking a scan."""

    def list_all_queues(self, vhost: Optional[str] = '/') -> List[Dict]:
        """Send a request to RabbitMQ api to list all the data queues.
        Args:
            vhost : String - Virtual host. Default value is '/'.
        """
        rabbitmq_api_path = utils.get_rabitmq_url(False)
        quoted_vhost = parse.quote_plus(vhost)
        queues_path = rabbitmq_api_path + f'/api/queues/{quoted_vhost}'
        queues =  utils.make_request('GET', queues_path)
        return queues


    def is_q_not_empty(self, queue: str) -> bool:
        """Check if a data queue is not empty.
        Agrs:
            queue: String - Data queue name
        Returns:
            Boolean - False if queue is empty, else True.
        """
        return queue['messages']  > 0 or queue['messages_unacknowledged'] > 0


    def are_queues_empty(self) -> bool:
        """Check if at least one data queue is not empty.
        Returns:
            Boolean - False if at least one data queue is not empty, else True.
        """
        queues = self.list_all_queues()
        for qu in queues:
            if self.is_q_not_empty(qu):
                return False
        return True

    def periodic_checks(self) -> None:
        """Periodically check the data queues, Only return of they are all empty."""
        time.sleep(SLEEP_SEC)
        i=0 #Just For Proof Of Concept.
        while True:
            print('Step : ', i) # JFPOC
            i+=1 # JFPOC
            if self.are_queues_empty():
                return
            time.sleep(SLEEP_SEC)

    def send_message(self, selector, message) -> None:
        """Uses the agent.emit method."""
        self.emit(selector, message)

    def kill_universe(self, universe_id: str) -> None:
        """Kill all containers belonging to universe with  universe_id."""
        print(f'Killing the universe. {universe_id}')
        client = docker.from_env()
        containers = client.containers.list()
        command = 'bin/sh --login -c \'echo $UNIVERSE_ID\''
        for container in containers:
            cmd_output = container.exec_run(command)
            container_universe_id = cmd_output.output.decode('utf-8')
            print('Container : ', container, ' output : ', cmd_output)
            if cmd_output.exit_code==0:
                if universe_id==container_universe_id:
                    container.kill()
            else:
                logger.error(cmd_output)

    def checking_process_with_timeout(self, timeout: int) -> None:
        """Method responsible for running periodic_checks inside a process with a time limit constraint.
        Args:
            timeout : time to wait before terminating the process.
        """
        check_scan_process = multiprocessing.Process(target=self.periodic_checks)
        check_scan_process.start()
        check_scan_process.join(timeout)

        if check_scan_process.is_alive():
            check_scan_process.kill()
            check_scan_process.join()

    def start(self) -> None:
        """Overriden method start responsible for the main logic of the agent."""
        self.checking_process_with_timeout(SCAN_DONE_TIMEOUT_SEC)

        channel = utils.get_rabbitmq_channel()
        channel.basic_publish(exchange='', routing_key='testQ', body='Mimicking scan done emission.')
        # 2 lines before should be changed to :
        #self.send_message('v2.report.event.scan_agent', {'scan_id': 1, 'source': '7', 'correlation_id': '42'})
        # after fixing the v2 protobuff msgs.

        # Sleep, to wait for the message to arrive, and not get empty queues.
        time.sleep(7)

        self.checking_process_with_timeout(POSTSCANE_DONE_TIMEOUT_SEC)

        channel.basic_publish(exchange='', routing_key='testQ', body='Mimicking post scan done emission.')
        #self.send_message('v2.report.event.post_scan_agent', {})

        universe_id = utils.get_universe_id()
        self.kill_universe(universe_id)


"""Next parts are only for testing purposes. will be removed later."""
from ostorlab.runtimes import definitions
agent_def = definitions.AgentDefinition(
    name='AgentName',
    out_selectors=['v3.healthcheck.ping']  #, 'v2.report.event.scan_agent']
)
agent_settings= definitions.AgentInstanceSettings(
    bus_url='amqp://guest:guest@localhost:55672/',
    bus_exchange_topic='/'
)

if __name__ == '__main__':
    trackerAgent = TrackerAgent(agent_def, agent_settings)
    trackerAgent.run()
