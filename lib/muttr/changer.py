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
Change the system default source and/or sink using PulseAudio.
"""

from logging import getLogger


log = getLogger(__name__)


class Changer:
    """
    Class implementing the command to change to a audio profile.

    :param Client client: Muttr PulseAudio client wrapper.
    :param list card_profile: Tuple with card name and profile to configure for
     this profile.
    :param str source: Name of the source to setup for this profile, if any.
    :param str sink: Name of the sink to setup for this profile, if any.
    """

    def __init__(self, client, card_profile=None, source=None, sink=None):
        self.client = client
        self.card_profile = card_profile
        self.source = source
        self.sink = sink

        assert card_profile or self.source or self.sink, (
            'Configure at least a card/profile, a source or a sink'
        )

    def change(self):
        """
        Execute action and change to this profile.
        """
        if self.card_profile:
            card_name, profile_desc = self.card_profile

            card = self.client.pulse.get_card_by_name(card_name)

            for profile in card.profile_list:
                if profile.description == profile_desc:
                    self.client.pulse.card_profile_set(
                        card,
                        profile,
                    )
                    break

            else:
                raise RuntimeError(
                    f'Profile {profile_desc!r} could not be found'
                )

        if self.source:
            for source in self.client.find_all_sources():
                if source.description == self.source:
                    self.client.pulse.default_set(source)
                    break
            else:
                raise RuntimeError(
                    f'Source {self.source!r} could not be found'
                )

        if self.sink:
            for sink in self.client.find_all_sinks():
                if sink.description == self.sink:
                    self.client.pulse.default_set(sink)
                    break
            else:
                raise RuntimeError(
                    f'Sink {self.sink!r} could not be found'
                )


__all__ = [
    'Changer',
]
