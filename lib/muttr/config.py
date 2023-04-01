# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2023 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Module to load application configuration and apply overrides.
"""

from pathlib import Path
from logging import getLogger

try:
    # Standard library, available in Python 3.11
    from tomllib import loads
except ImportError:
    from tomli import loads

from objns import Namespace
from pkg_resources import resource_string


log = getLogger(__name__)


def load_config(
    configs,
    systemconfs=(
        '/etc/muttr/config.toml',
        '~/.config/muttr/config.toml',
    ),
):
    """
    Load application default configuration and apply overrides from the the
    given configurations files, in the order given.

    :param list configs: List of paths to user configuration files (TOML).
    :param list systemconfs: List of paths to system configuration files.

    :return: The final, overriden and merged configuration.
    :rtype: dict
    """
    config = Namespace(loads(
        resource_string(
            __package__, 'data/config.toml'
        ).decode(encoding='utf-8')
    ))

    for systemconf in systemconfs:
        systemconf = Path(systemconf).expanduser()

        if systemconf.is_file():
            log.info(f'Found {systemconf} file. Reading ...')

            config.update(loads(
                systemconf.read_text(encoding='utf-8')
            ))

    for configfile in configs:
        config.update(loads(
            configfile.read_text(encoding='utf-8')
        ))

    return config.muttr


__all__ = [
    'load_config',
]
