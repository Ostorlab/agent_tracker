"""Tracker Agent : Agent responsible for tracking a scan, e.g., status, data queues."""
from time import sleep
import logging
import requests
import json
from urllib import parse
from typing import Dict, Optional

import ostorlab
from ostorlab.agent import agent


class AuthenticationError(Exception):
    """Authentication Error."""


logger = logging.getLogger(__name__)

SLEEP_SEC = 2
class TrackerAgent(agent.Agent):
    """Agent responsible for tracking a scan."""

    def _make_request(self, method: str, fullpath: str, data: Optional[Dict[str, str]] = None):
        logger.info('Request %s %s %s', method, fullpath, data)
        response = requests.request(method, fullpath, data=json.dumps(data))
        if response.status_code not in [200, 201, 204]:
            logger.error('Received %i %s', response.status_code, response.content)
            raise AuthenticationError(response.reason)
        elif response.status_code == 200:
            return response.json()
        else:
            return None


    #rabitmq_url='localhost:8088', user='guest', pwd='guest'
    def list_all_queues(self, vhost='/'):
        full_path = "http://guest:guest@localhost:15672/api/queues/"
        #quoted_vhost = parse.quote_plus(vhost)
        queues =  self._make_request('GET', full_path)
        return queues

    def is_q_not_empty(self, queue):
        return queue['messages']  > 0 or queue['messages_unacknowledged'] > 0

    def are_queues_empty(self):
        queues = self.list_all_queues()
        for qu in queues:
            if self.is_q_not_empty(qu):
                return False
        return True

    def periodic_checks(self):
        sleep(SLEEP_SEC)
        while True:
            if self.are_queues_empty():
                return
            sleep(SLEEP_SEC)


    def kill_universe(self):
        print('Killing the universe.')


    def start(self) -> None:

        self.periodic_checks()

        #self.emit('v2.report.event.scan_agent', {'scan_id': 1, 'source': '7', 'correlation_id': '42'})
        self.emit('v3.healthcheck.ping', {'body': 'Hello World!'})

        self.periodic_checks()

        self.kill_universe()



"""Next parts are only for testing purposes. will be removed later."""
from ostorlab.runtimes import definitions
agent_def = definitions.AgentDefinition(
    name='AgentName',
    out_selectors=['v3.healthcheck.ping']  #, 'v2.report.event.scan_agent']
)
agent_settings= definitions.AgentInstanceSettings(
    bus_url='amqp://guest:guest@localhost:55672/',
    bus_exchange_topic='*'
)

if __name__ == '__main__':
    trackerAgent = TrackerAgent(agent_def, agent_settings)
    trackerAgent.run()
