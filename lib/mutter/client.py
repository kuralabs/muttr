# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 KuraLabs S.R.L
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


log = getLogger(__name__)


class Client:

    def __init__(self, **kwargs):
        self.pulse = Pulse(**kwargs)

    def show_system(self, logger=log.info):

        info = self.pulse.server_info()
        logger(
            f'Connected to PulseAudio Server '
            f'{info.server_name!r} v{info.server_version} as '
            f'{info.user_name}@{info.host_name}'
        )

        logger('Sources found:')
        for source in self.find_all_sources():
            logger(f'    -> {source.description}')

            profiles = sorted(
                self.pulse.card_info(source.card).profile_list,
                key=lambda profile: profile.description,
            )
            if len(profiles) > 1:
                logger(f'         Profiles:')
                for profile in profiles:
                    logger(f'         -> {profile.description}')

        logger('Sinks found:')
        for source in self.find_all_sinks():
            logger(f'    -> {source.description}')

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
