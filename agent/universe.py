"""Module responsible for universe-related methods."""
import logging

import docker

logger = logging.getLogger(__name__)


def kill_universe(universe_id: str) -> None:
    """remove a service belonging to universe with universe_id."""
    client = docker.from_env()
    services = client.services.list()
    logger.info('Stopping the scan services')
    for s in services:
        service_env_variables = s.attrs['Spec']['Labels']
        if service_env_variables.get('ostorlab.universe') == universe_id:
            s.remove()

    logger.info('Stopping the scan network')
    networks = client.networks.list()
    for network in networks:
        network_labels = network.attrs['Labels']
        if network_labels.get('ostorlab.universe') == universe_id:
            network.remove()

    logger.info('Stopping the scan configs')
    configs = client.configs.list()
    for config in configs:
        config_labels = config.attrs['Spec']['Labels']
        if config_labels.get('ostorlab.universe') == universe_id:
            config.remove()
