"""Tests for the tracker agent.
(TODO) Still needs tests.
"""
import pytest
import time

from ostorlab.agent.testing.mock_agent import agent_mock # pylint: disable=W0611

import src.agent as agent_tracker
from src import data_queues

def testTrackerAgentCheckQueueNotEmpty_whenQueueIsNotEmpty_returnTrue():
    dummy_queue = {
        'auto_delete': False,
        'message_bytes_ready': 34,
        'vhost': '/',
        'name': 'aliveness-test',
        'messages': 42,
        'messages_unacknowledged': 0
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is True

def testTrackerAgentCheckQueueNotEmpty_whenQueueIsEmpty_returnFalse():
    dummy_queue = {
        'auto_delete': False,
        'message_bytes_ready': 34,
        'vhost': '/',
        'name': 'aliveness-test',
        'messages': 0,
        'messages_unacknowledged': 0
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is False

@pytest.mark.asyncio
def testTrackerAgentLogic_whenQueuesAreNotEmpty_killProcessesAndSend4Messages(mocker, agent_mock, tracker_agent): # pylint: disable=W0621
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

@pytest.mark.asyncio
def testTrackerLogic_whenQueuesAreEmpty_send2messages(mocker, agent_mock, tracker_agent): # pylint: disable=W0621
    mocker.patch('data_queues.are_queues_empty', return_value=True)
    mocker.patch('universe.kill_universe', return_value=None)
    mocker.patch('time.sleep', side_effect=time.sleep(0.01))

    tracker_agent.run()

    assert len(agent_mock) == 2
    assert agent_mock[0].selector == 'v3.report.event.scan.done'
    assert agent_mock[1].selector == 'v3.report.event.post_scan.done'

@pytest.mark.asyncio
def testTimeoutQueuesChecking_whenQueuesStartEmptyAndGetMsgs_send3Messages(mocker, agent_mock, tracker_agent): # pylint: disable=W0621
    mocker.patch('data_queues.are_queues_empty', return_value=True)
    mocker.patch('time.sleep', side_effect=time.sleep(0.01))
    mocker.patch.object(agent_tracker, 'SCAN_DONE_TIMEOUT_SEC', 0.05)
    mocker.patch.object(agent_tracker, 'POSTSCANE_DONE_TIMEOUT_SEC', 0.05)

    try:
        tracker_agent.timeout_queues_checking(0.1)
    except TimeoutError:
        tracker_agent.emit('v3.report.event.scan.timeout', {})
    tracker_agent.emit('v3.report.event.scan.done', {})
    mocker.patch('data_queues.are_queues_empty', return_value=False)
    try:
        tracker_agent.timeout_queues_checking(0.1)
    except TimeoutError:
        tracker_agent.emit('v3.report.event.post_scan.timeout', {})
    tracker_agent.emit('v3.report.event.post_scan.done', {})

    assert len(agent_mock) == 3
    assert agent_mock[0].selector == 'v3.report.event.scan.done'
    assert agent_mock[1].selector == 'v3.report.event.post_scan.timeout'
    assert agent_mock[2].selector == 'v3.report.event.post_scan.done'
