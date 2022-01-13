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
            service_env_variables = s.attrs['Spec']['TaskTemplate']['ContainerSpec']['Env']
            for variable in service_env_variables:
                if 'UNIVERSE' in variable and variable.split('=')[-1] == universe_id:
                    s.remove()
        except KeyError:
            logger.error('The environement variable : UNIVERSE does not exist.')
