# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 KuraLabs S.R.L
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
Client to interact with the PulseAudio server.
"""

from logging import getLogger

from pulsectl import Pulse
from pkg_resources import get_distribution


log = getLogger(__name__)


class Client:
    """
    Muttr PulseAudio client wrapper.

    Basically implements PulseAudio utilities used by action classes.
    """

    def __init__(self, **kwargs):
        self.pulse = Pulse(**kwargs)

    def show_system(self, logger=log.info):
        """
        Print this system's audio cards, profiles, sinks and sources tree.

        :param logger: Function to print the tree.
        """

        info = self.pulse.server_info()
        logger(
            f'Connected to PulseAudio Server '
            f'{info.server_name!r} v{info.server_version} as '
            f'{info.user_name}@{info.host_name} '
            f'using pulsectl version {get_distribution("pulsectl")}'
        )

        for card in sorted(
            self.pulse.card_list(),
            key=lambda c: c.index,
        ):
            logger(f'Card #{card.index}: {card.name!r}')
            logger(f'  Active profile: {card.profile_active.name!r}')

            logger('  Available Profiles:')
            for profile in sorted(
                card.profile_list,
                key=lambda p: p.priority,
                reverse=True,
            ):
                logger(f'    - {profile.name!r}')
                logger(
                    f'      "{profile.description}" '
                    f'[priority={profile.priority}]'
                )

            logger('  Sources:')
            for source in sorted(
                (
                    source for source in
                    self.pulse.source_list()
                    if (
                        source.card == card.index and
                        source.monitor_of_sink_name is None
                    )
                ),
                key=lambda s: s.index,
            ):
                logger(f'    - {source.name!r}')
                logger(
                    f'      "{source.description}" '
                    f'[index={source.index}] '
                    f'[{source.volume}]'
                )

            logger('  Sinks:')
            for sink in sorted(
                (
                    sink for sink in
                    self.pulse.sink_list()
                    if sink.card == card.index
                ),
                key=lambda s: s.name,
            ):
                logger(f'    - {sink.name!r}')
                logger(
                    f'      "{sink.description}" '
                    f'[index={sink.index}] '
                    f'[{sink.volume}]'
                )

            logger('--')

    def find_all_sources(self):
        """
        Return the list of sources found in the system.
        """
        return sorted(
            (
                source
                for source in self.pulse.source_list()
                if source.monitor_of_sink_name is None
            ),
            key=lambda s: s.description,
        )

    def find_all_sinks(self):
        """
        Return the list of sinks found in the system.
        """
        return sorted(
            self.pulse.sink_list(),
            key=lambda s: s.description,
        )


__all__ = [
    'Client',
]
