"""Tests for the tracker agent.
(TODO) Still needs tests.
"""
from ostorlab.agent import definitions as agent_definitions
from ostorlab.runtimes import definitions as runtime_definitions
from ostorlab import agent
from ostorlab.agent.testing.mock_agent import agent_mock
import agent as agent_tracker

import data_queues

def _testTrackerAgentCheckQueueNotEmpty_whenQueueIsNotEmpty_returnTrue():
    dummy_queue = {
        'auto_delete': False,
        'message_bytes_ready': 34,
        'vhost': '/',
        'name': 'aliveness-test',
        'messages': 42,
        'messages_unacknowledged': 0
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is True

def _testTrackerAgentCheckQueueNotEmpty_whenQueueIsEmpty_returnFalse():
    dummy_queue = {
        'auto_delete': False,
        'message_bytes_ready': 34,
        'vhost': '/',
        'name': 'aliveness-test',
        'messages': 0,
        'messages_unacknowledged': 0
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is False

import time

def testTrackerAgentLogic_whenQueuesAreNotEmpty_killProcessesAndSend4Messages(mocker, agent_mock, tracker_agent):
    mocker.patch('data_queues.are_queues_empty', return_value=False)
    mocker.patch('universe.kill_universe', return_value=None)
    mocker.patch.object(agent_tracker, 'SCAN_DONE_TIMEOUT_SEC', 0.05)
    mocker.patch.object(agent_tracker, 'POSTSCANE_DONE_TIMEOUT_SEC', 0.05)
    mocker.patch.object(data_queues, 'SLEEP_SEC', 0.01)
    tracker_agent.run()
    # Should timeout twice, for scan done & post scan done.
    # Data queue from agent_mock fixture should have 4 messages:
    #Scan timeout, scan done, post scan timeout, & post scan done.
    assert len(agent_mock) == 4
    assert agent_mock[0].selector == 'v3.report.event.scan.timeout'
    assert agent_mock[1].selector == 'v3.report.event.scan.done'
    assert agent_mock[2].selector == 'v3.report.event.post_scan.timeout'
    assert agent_mock[3].selector == 'v3.report.event.post_scan.done'

def testCheckingProcessWithTimeout_whenQueuesAreEmpty_send2messages(mocker, agent_mock, tracker_agent):
    mocker.patch('data_queues.are_queues_empty', return_value=True)
    mocker.patch('universe.kill_universe', return_value=None)

    tracker_agent.run()

    assert len(agent_mock) == 2
    assert agent_mock[0].selector == 'v3.report.event.scan.done'
    assert agent_mock[1].selector == 'v3.report.event.post_scan.done'