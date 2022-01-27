"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
import logging
import multiprocessing

from ostorlab.agent import agent
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions

from agent import data_queues
from agent import universe

logger = logging.getLogger(__name__)


class TrackerAgent(agent.Agent):
    """Agent responsible for tracking a scan."""

    def __init__(self,
                 agent_definition: agent_definitions.AgentDefinition,
                 agent_instance_definition: runtime_definitions.AgentSettings,
                 scan_done_timeout_sec: int,
                 postscane_done_timeout_sec: int
                 ) -> None:
        """Inits the tracker agent."""
        super().__init__(agent_definition, agent_instance_definition)
        self.scan_done_timeout_sec = scan_done_timeout_sec
        self.postscane_done_timeout_sec = postscane_done_timeout_sec

    def start(self) -> None:
        """Overriden method start responsible for :
            Periodically checking the data queues state
                In case checking exceeded the time limit, a scan-timeout message is sent.
                A scan-done message is sent.
            Since some other agents, might be waiting for the scan-done/timeout messages,
            another periodic check is required.
            This time, sending postscan-done/timeout messages.
            Finally a clean-up is executed to stop all services belonging to the current universe.
        """

        try:
            self.timeout_queues_checking(self.scan_done_timeout_sec)
        except TimeoutError:
            self.emit('v3.report.event.scan.timeout', {})

        self.emit('v3.report.event.scan.done', {})

        try:
            self.timeout_queues_checking(self.postscane_done_timeout_sec)
        except TimeoutError:
            self.emit('v3.report.event.post_scan.timeout', {})

        self.emit('v3.report.event.post_scan.done', {})

        universe_id = self.universe
        universe.kill_universe(universe_id)

    def timeout_queues_checking(self, timeout: int) -> None:
        """Method responsible for running check_queues_periodically inside a process with a time limit constraint.
        Kills the process and raises an exception in case it exceeded the time limit.
        Args:
            timeout: time to wait before terminating the process.
        Raises:
            TimeoutError: In case the process exceeded the time limit
        """
        check_scan_process = multiprocessing.Process(
            target=data_queues.check_queues_periodically,
            args=(self.bus_managment_url, self.bus_vhost)
        )
        check_scan_process.start()
        check_scan_process.join(timeout)

        if check_scan_process.is_alive():
            check_scan_process.kill()
            check_scan_process.join()
            raise TimeoutError()
