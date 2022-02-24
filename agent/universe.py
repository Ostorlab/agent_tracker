"""Module responsible for universe-related methods."""
import logging

import docker


logger = logging.getLogger(__name__)


def kill_universe(universe_id: str) -> None:
    """remove a service belonging to universe with universe_id."""
    client = docker.from_env()
    services = client.services.list()
    logger.info('stopping the scan services')
    for s in services:
        service_env_variables = s.attrs['Spec'].get('Labels') or {}
        if service_env_variables.get('ostorlab.universe') == universe_id:
            s.remove()

    logger.info('stopping the scan network')
    networks = client.networks.list()
    for network in networks:
        network_labels = network.attrs.get('Labels') or {}
        if network_labels.get('ostorlab.universe') == universe_id:
            network.remove()

    logger.info('stopping the scan configs')
    configs = client.configs.list()
    for config in configs:
        config_labels = config.attrs['Spec'].get('Labels') or {}
        if config_labels.get('ostorlab.universe') == universe_id:
            config.remove()
