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
[Un]Mute all sound sources using PulseAudio.
"""

from logging import getLogger


log = getLogger(__name__)


class Muter:
    """
    Class implementing the command to mute or unmute the system.
    """

    def __init__(self, client, sources=None):
        self.client = client
        self.sources = sources

    def find(self):
        """
        Find all sources relevant to the mutting action.

        :return: List of sources in this system relevant to the mute action.
        :rtype: list
        """
        if not self.sources:
            return self.client.find_all_sources()

        return [
            source
            for source in self.client.find_all_sources()
            if source.description in self.sources
        ]

    def is_muted(self):
        """
        Check if all relevant sources in the system are muted.

        :return: True if all sources are muted.
        :rtype: bool
        """
        return all(
            bool(source.mute)
            for source in self.find()
        )

    def mute(self):
        """
        Mute all relevant sources in the system.
        """
        for source in self.find():
            self.client.pulse.mute(source, mute=True)
            self.client.pulse.volume_set_all_chans(source, 0.0)

    def unmute(self):
        """
        Unmute all relevant sources in the system.
        """
        for source in self.find():
            self.client.pulse.mute(source, mute=False)
            self.client.pulse.volume_set_all_chans(source, 1.0)


__all__ = [
    'Muter',
]
