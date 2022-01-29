"""Module responsible for universe-related methods."""
import logging

import docker

logger = logging.getLogger(__name__)


def kill_universe(universe_id: str) -> None:
    """remove a service belonging to universe with universe_id."""
    client = docker.from_env()
    services = client.services.list()
    for s in services:
        try:
            service_env_variables = s.attrs['Spec']['Labels']
            if 'ostorlab.universe' in service_env_variables and\
                    service_env_variables['ostorlab.universe'] == universe_id:
                s.remove()
        except KeyError:
            logger.error('The environement variable : OSTORLAB.UNIVERSE does not exist.')
