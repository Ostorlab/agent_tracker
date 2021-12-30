"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""

import ostorlab

class TrackerAgent(ostorlab.Agent):
    """Agent responsible for tracking a scan."""

    def process(self, message: ostorlab.Message) -> None:
        """TODO (author): add your description here.

        Args:
            message:

        Returns:

        """
        # TODO (author): implement agent logic here.
        self.emit('v3.healthcheck.ping', {'body': 'Hello World!'})