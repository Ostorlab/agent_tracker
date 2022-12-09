"""Tests for the tracker agent."""
import os
from unittest import mock

import pytest
from ostorlab.runtimes.local.models import models

from agent import data_queues


def testTrackerAgentCheckQueueNotEmpty_whenQueueIsNotEmpty_returnTrue():
    """Test for the method responsible for checking if a data queue is empty."""
    dummy_queue = {
        "auto_delete": False,
        "message_bytes_ready": 34,
        "vhost": "/",
        "name": "aliveness-test",
        "messages": 42,
        "messages_unacknowledged": 0,
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is True


def testTrackerAgentCheckQueueNotEmpty_whenQueueIsEmpty_returnFalse():
    """Test for the method responsible for checking if a data queue is empty."""
    dummy_queue = {
        "auto_delete": False,
        "message_bytes_ready": 34,
        "vhost": "/",
        "name": "aliveness-test",
        "messages": 0,
        "messages_unacknowledged": 0,
    }

    assert data_queues.is_queue_not_empty(dummy_queue) is False


@pytest.mark.asyncio
@mock.patch(
    "ostorlab.runtimes.local.models.models.ENGINE_URL",
    "sqlite:////tmp/ostorlab_db1.sqlite",
)
def testTrackerAgentLogic_whenQueuesAreNotEmpty_killProcessesAndSend4Messages(
    mocker, agent_mock, tracker_agent, requests_mock
):
    """Test for the life cycle of the agent tracker.
    Case : The data queues start full.
    The agent should keep checking if the scan is done,
    then time-out, emits a message : scan_done_timeout
    emits another message : scan_done.
    Checks again if the data queues are empty (they are still full).
    So, it should timeout, emits a message : post_scan_done_timeout,
    and another message : post_scan_done.
    """
    # breakpoint()
    path = "http://guest:guest@localhost:15672/api/queues/%2F"
    requests_mock.get(
        path,
        json=[
            {"name": "queue1", "messages": 42, "messages_unacknowledged": 0},
            {"name": "queue2", "messages": 0, "messages_unacknowledged": 0},
        ],
    )
    mocker.patch("agent.tracker_agent.universe.kill_universe", return_value=None)
    mocker.patch.object(data_queues, "SLEEP_SEC", 0.01)

    tracker_agent.run()

    assert len(agent_mock) == 4
    assert agent_mock[0].selector == "v3.report.event.scan.timeout"
    assert agent_mock[1].selector == "v3.report.event.scan.done"
    assert agent_mock[2].selector == "v3.report.event.post_scan.timeout"
    assert agent_mock[3].selector == "v3.report.event.post_scan.done"
    with models.Database() as session:
        assert (
            session.query(models.Scan).get(os.getenv("UNIVERSE")).progress
            == models.ScanProgress.DONE
        )


@pytest.mark.asyncio
def testTrackerLogic_whenQueuesAreEmpty_send2messages(
    mocker, agent_mock, tracker_agent, requests_mock
):
    """Test for the life cycle of the agent tracker.
    Case : The data queues start empty.
    The agent should automatically emit a message : scan_done.
    Checks again if the data queues are empty(they are empty).
    So, it should automatically emit a message : post_scan_done.
    """
    mocker.patch("agent.tracker_agent.universe.kill_universe", return_value=None)
    path = "http://guest:guest@localhost:15672/api/queues/%2F"
    requests_mock.get(
        path,
        json=[
            {"name": "queue1", "messages": 0, "messages_unacknowledged": 0},
            {"name": "queue2", "messages": 0, "messages_unacknowledged": 0},
        ],
    )

    tracker_agent.run()

    assert len(agent_mock) == 2
    assert agent_mock[0].selector == "v3.report.event.scan.done"
    assert agent_mock[1].selector == "v3.report.event.post_scan.done"
