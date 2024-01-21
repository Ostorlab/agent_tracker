"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
import logging
import multiprocessing
import os
import time

from ostorlab.agent import agent
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions
from ostorlab.runtimes.local.models import models
from rich import logging as rich_logging

from agent import data_queues
from agent import universe

logging.basicConfig(
    format="%(message)s",
    datefmt="[%X]",
    handlers=[rich_logging.RichHandler(rich_tracebacks=True)],
    level="INFO",
    force=True,
)
logger = logging.getLogger(__name__)


class TrackerAgent(agent.Agent):
    """Agent responsible for tracking a scan."""

    def __init__(
        self,
        agent_definition: agent_definitions.AgentDefinition,
        agent_settings: runtime_definitions.AgentSettings,
    ) -> None:
        """Inits the tracker agent."""
        super().__init__(agent_definition, agent_settings)
        self.init_sleep_seconds = self.args.get("init_sleep_seconds")
        self.scan_done_timeout_sec = self.args.get("scan_done_timeout_sec")
        self.postscane_done_timeout_sec = self.args.get("postscane_done_timeout_sec")

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
            time.sleep(self.init_sleep_seconds)
            self.timeout_queues_checking(self.scan_done_timeout_sec)
        except TimeoutError:
            logger.info("scan timeout after: %s s", str(self.scan_done_timeout_sec))
            self.emit("v3.report.event.scan.timeout", {})

        self.emit("v3.report.event.scan.done", {})

        try:
            self.timeout_queues_checking(self.postscane_done_timeout_sec)
        except TimeoutError:
            logger.info(
                "post scan timeout after: %s", str(self.postscane_done_timeout_sec)
            )
            self.emit("v3.report.event.post_scan.timeout", {})

        self.emit("v3.report.event.post_scan.done", {})
        logger.info("updating scan status to done.")
        self._set_scan_progress(models.ScanProgress.DONE)
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
            args=(self.bus_managment_url, self.bus_vhost),
        )
        check_scan_process.start()
        check_scan_process.join(timeout)

        if check_scan_process.is_alive():
            check_scan_process.kill()
            check_scan_process.join()
            raise TimeoutError()

    def _set_scan_progress(self, progress: str):
        """Persist the scan progress in the database
        Args:
            progress: scan progress to persist.
        """
        with models.Database() as session:
            scan = session.query(models.Scan).get(os.getenv("UNIVERSE"))
            if scan is not None:
                scan.progress = progress
                session.commit()
            else:
                logger.error(f"Scan for {os.getenv('UNIVERSE')} does not exist.")


if __name__ == "__main__":
    logger.info("starting agent..")
    TrackerAgent.main()
