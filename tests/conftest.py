"""Pytest fixture for the tracker agent."""
import pytest

import agent as agent_tracker
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions

SCAN_DONE_TIMEOUT_SEC = 0.2
POSTSCANE_DONE_TIMEOUT_SEC = 0.2


@pytest.fixture(scope='function', name='tracker_agent')
def fixture_tracker_agent():
    """Instantiate a tracker agent."""
    definition = agent_definitions.AgentDefinition(
        name='agent_tracker',
        out_selectors=[
            'v3.report.event.scan.done',
            'v3.report.event.scan.timeout',
            'v3.report.event.post_scan.timeout',
            'v3.report.event.post_scan.done'
            ])
    settings = runtime_definitions.AgentSettings(
        key='agent_tracker_key',
        bus_url='NA',
        bus_exchange_topic='NA',
        bus_managment_url='http://guest:guest@localhost:15672',
        bus_vhost='/',
        )

    agent = agent_tracker.TrackerAgent(definition, settings, SCAN_DONE_TIMEOUT_SEC, POSTSCANE_DONE_TIMEOUT_SEC)
    return agent
