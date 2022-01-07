"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
import multiprocessing
import logging

from ostorlab.agent import agent
from src import data_queues
from src import universe


logger = logging.getLogger(__name__)
SCAN_DONE_TIMEOUT_SEC = 10
POSTSCANE_DONE_TIMEOUT_SEC = 10


class TrackerAgent(agent.Agent):
    """Agent responsible for tracking a scan."""

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
            self.timeout_queues_checking(SCAN_DONE_TIMEOUT_SEC)
        except TimeoutError:
            self.emit('v3.report.event.scan.timeout', {})

        self.emit('v3.report.event.scan.done', {})

        try:
            self.timeout_queues_checking(POSTSCANE_DONE_TIMEOUT_SEC)
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
        check_scan_process = multiprocessing.Process(target=data_queues.check_queues_periodically, args=(self.bus_url,))
        check_scan_process.start()
        check_scan_process.join(timeout)

        if check_scan_process.is_alive():
            check_scan_process.kill()
            check_scan_process.join()
            raise TimeoutError
