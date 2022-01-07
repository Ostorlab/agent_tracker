"""
    Dummy conftest.py for template_agent.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""
import pytest

import src.agent as agent_tracker
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions

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
        bus_exchange_topic='NA')

    agent = agent_tracker.TrackerAgent(definition, settings)
    return agent
