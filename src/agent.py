"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
import multiprocessing
import time
import logging
from urllib import parse
from typing import Any, Dict, Optional, List

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


    def _is_q_not_empty(self, queue: str) -> bool:
        """Check if a data queue is not empty.
        Agrs:
            queue: String - Data queue name
        Returns:
            Boolean - False if queue is empty, else True.
        """
        return queue['messages']  > 0 or queue['messages_unacknowledged'] > 0


    def _are_queues_empty(self) -> bool:
        """Check if at least one data queue is not empty.
        Returns:
            Boolean - False if at least one data queue is not empty, else True.
        """
        queues = self.list_all_queues()
        for qu in queues:
            if self._is_q_not_empty(qu):
                return False
        return True


    def _periodic_checks(self) -> None:
        """Periodically check the data queues, Only return if they are all empty."""
        while True:
            if self._are_queues_empty():
                return
            time.sleep(SLEEP_SEC)


    def send_message(self, selector: str, data: Dict[str, Any]) -> None:
        """Uses the agent.emit method."""
        self.emit(selector, data)


    def checking_process_with_timeout(self, timeout: int, selector: str) -> None:
        """Method responsible for running periodic_checks inside a process with a time limit constraint.
        Kills the process and emits a message in case it exceeded the time limit.
        Args:
            timeout : time to wait before terminating the process.
        """
        check_scan_process = multiprocessing.Process(target=self._periodic_checks)
        check_scan_process.start()
        check_scan_process.join(timeout)

        if check_scan_process.is_alive():
            check_scan_process.kill()
            check_scan_process.join()
            self.send_message(selector, {})


    def kill_universe(self, universe_id: str) -> None:
        """remove a service belonging to universe with universe_id."""
        client = docker.from_env()
        services = client.services.list()
        for s in services:
            try:
                service_env_variables = s.attrs['Spec']['TaskTemplate']['ContainerSpec']['Env']
                for variable in service_env_variables:
                    if 'UNIVERSE_ID' in variable and variable.split('=')[-1]==universe_id:
                        s.remove()
            except KeyError:
                logger.error('The environement variables do not exist.')


    def start(self) -> None:
        """Overriden method start responsible for the main logic of the agent."""

        self.checking_process_with_timeout(
            SCAN_DONE_TIMEOUT_SEC,
            'v3.report.event.scan.timeout'
            )

        self.send_message('v3.report.event.scan.done', {})

        self.checking_process_with_timeout(
            POSTSCANE_DONE_TIMEOUT_SEC,
            'v3.report.event.post_scan.timeout'
        )

        self.send_message('v3.report.event.post_scan.done', {})

        universe_id = utils.get_universe_id()
        self.kill_universe(universe_id)
