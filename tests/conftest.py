"""Pytest fixture for the tracker agent."""
import pytest
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions

from agent import tracker_agent as agent_tracker

SCAN_DONE_TIMEOUT_SEC = 1
POSTSCAN_DONE_TIMEOUT_SEC = 1


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
        ],
        args=[
            {
                'name': 'init_sleep_seconds',
                'type': 'number',
                'value': SCAN_DONE_TIMEOUT_SEC,
                'description': 'blabla'
            },
            {
                'name': 'scan_done_timeout_sec',
                'type': 'number',
                'value': SCAN_DONE_TIMEOUT_SEC,
                'description': 'blabla'
            },
            {
                'name': 'postscane_done_timeout_sec',
                'type': 'number',
                'value': POSTSCAN_DONE_TIMEOUT_SEC,
                'description': 'blabla'
            }
        ])
    settings = runtime_definitions.AgentSettings(
        key='agent_tracker_key',
        bus_url='NA',
        bus_exchange_topic='NA',
        bus_vhost='/',
    )

    agent = agent_tracker.TrackerAgent(definition, settings)
    return agent
