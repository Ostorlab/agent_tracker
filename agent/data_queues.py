"""Module responsible for handling the data queues, listing them & checking their states."""
import time
from typing import Dict, List, Optional
from urllib import parse

from agent import request_sender

SLEEP_SEC = 3
MAX_COUNT = 5


def list_all_queues(path: str, vhost: Optional[str] = '/') -> List[Dict]:
    """Send a request to RabbitMQ api to list all the data queues.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
        vhost: Virtual host of the RabbitMQ.
    Returns:
        List of all the data queues.
    """
    quoted_vhost = parse.quote_plus(vhost)
    queues_path = path + f'/api/queues/{quoted_vhost}'
    queues = request_sender.make_request('GET', queues_path)
    return queues


def is_queue_not_empty(queue: str) -> bool:
    """Check if a data queue is not empty.
    Agrs:
        queue: Data queue name
    Returns:
        False if queue is empty, else True.
    """
    return queue['messages'] > 0 or queue['messages_unacknowledged'] > 0


def are_queues_empty(path: str, vhost: str) -> bool:
    """Check if at least one data queue is not empty.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
    Returns:
        False if at least one data queue is not empty, else True.
    """
    queues = list_all_queues(path, vhost)
    for queue in queues:
        if is_queue_not_empty(queue):
            return False
    return True


def confirm_queues_are_empty(path: str, vhost: str, max_count: int) -> bool:
    """Confirms that the queues are empty.
    Tries to lower the probability of a message in transit by introducing a max_count variable.
    The method should check for 'max_count' number of times before it can confirm that the queues are empty.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
        vhost: Virtual host of the RabbitMQ.
        max_count: Number of times to check before returning.
    Returns:
        False if at least one data queue is not empty, else True.
    """
    counter = 0
    while counter < max_count:
        counter += 1
        if not are_queues_empty(path, vhost):
            return False
    return True


def check_queues_periodically(path: str, vhost: str) -> None:
    """Periodically check the data queues, Only return if they are all empty.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
    """
    while not confirm_queues_are_empty(path, vhost, MAX_COUNT):
        time.sleep(SLEEP_SEC)