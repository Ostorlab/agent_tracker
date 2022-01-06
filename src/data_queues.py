"""Module responsible for handling the data queues, listing them & checking their states."""
from typing import Dict, List, Optional
import time
from urllib import parse

import request_sender

SLEEP_SEC = 3

def list_all_queues(path: str, vhost: Optional[str] = '/') -> List[Dict]:
    """Send a request to RabbitMQ api to list all the data queues.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
        vhost: Virtual hostof the RabbitMQ.
    """
    quoted_vhost = parse.quote_plus(vhost)
    queues_path = path + f'/api/queues/{quoted_vhost}'
    queues =  request_sender.make_request('GET', queues_path)
    return queues


def is_queue_not_empty(queue: str) -> bool:
    """Check if a data queue is not empty.
    Agrs:
        queue: Data queue name
    Returns:
        False if queue is empty, else True.
    """
    return queue['messages']  > 0 or queue['messages_unacknowledged'] > 0


def are_queues_empty(path:str) -> bool:
    """Check if at least one data queue is not empty.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
    Returns:
        False if at least one data queue is not empty, else True.
    """
    queues = list_all_queues(path)
    for queue in queues:
        if is_queue_not_empty(queue):
            return False
    return True


def check_queues_periodically(path: str) -> None:
    """Periodically check the data queues, Only return if they are all empty.
    Args:
        path: Path to the RabbitMQ management api to send the request to.
    """
    while not are_queues_empty(path):
        time.sleep(SLEEP_SEC)
