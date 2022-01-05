"""Utils for the tracker agent.
Provides helping constants & methods like rabbitMQ credentials, URL,
and sending requests for the rabbitMQ management API.
"""
import os
import requests
import json
import logging
from typing import Dict, Optional


logger = logging.getLogger(__name__)

USERNAME = 'guest'
PASSWORD = 'guest'
HOST = 'localhost'
PORT = '15672'

class AuthenticationError(Exception):
    """Authentication Error."""

def make_request(method: str, path: str, data: Optional[Dict[str, str]] = None):
    """Method that sends an HTTP request.
    Args:
        method : Required - One of HTTP requests, e.g., GET, POST.
        path : Required - Where to send the request to.
        data : Optional - Dictionary of data to be sent in the request.
    Returns:
        response : in json format if status code is 200
        None : if status code is 201 or 204
    Raises:
        AuthenticationError: if status code is not successful (200, 201, 204)
    """
    logger.info('Request %s %s %s', method, path, data)
    response = requests.request(method, path, data=json.dumps(data))
    if response.status_code not in [200, 201, 204]:
        logger.error('Received %i %s', response.status_code, response.content)
        raise AuthenticationError(response.reason)
    elif response.status_code == 200:
        return response.json()
    else:
        return None


def get_rabitmq_url(use_https: bool) -> str:
    """Return URL to RabbitMQ management API.
    Args:
        use_https: Boolean : Usage of HTTPS
    """
    if use_https:
        return f'https://{USERNAME}:{PASSWORD}@{HOST}:{PORT}'
    return f'http://{USERNAME}:{PASSWORD}@{HOST}:{PORT}'

def get_universe_id() -> str:
    """Method that returns the universe_id, stored as an environment variable.
    Returns:
        The universe id.
    Raises:
        KeyError : In case the environment variable(universe_id) does not exist.
    """
    try:
        return os.environ['UNIVERSE_ID']
    except KeyError:
        logger.error('The UNIVERSE_ID variable does not exist in the current environment.')
