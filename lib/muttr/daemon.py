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
Daemon to listen on keyboard events to perform actions.
"""

from itertools import cycle
from logging import getLogger
from collections import OrderedDict

from objns import Namespace
from pynput.keyboard import GlobalHotKeys
from pkg_resources import resource_filename

from .muter import Muter
from .changer import Changer
from .sound import play_sound


log = getLogger(__name__)


class Daemon:
    """
    Muttr daemon class to listen on keyboard events.

    :param Client client: Muttr PulseAudio client wrapper.
    :param Namespace config: System's configuration.
    :param bool sounds: Enable or disable sound playback.
    """

    def __init__(self, client, config, sounds):
        self.client = client
        self.config = config
        self.sounds = sounds

        self._muter = Muter(client, sources=config.muter.sources)
        self._changers = OrderedDict()

        self._hotkeys = {}

        # Create global hot keys controls
        for option in [
            'hotkey_mute',
            'hotkey_unmute',
            'hotkey_mute_toggle',
            'hotkey_change_cycle',
        ]:
            hotkey = config.daemon[option]
            if not hotkey:
                continue

            self._hotkeys[hotkey] = self.create_global_activate(hotkey, option)
            log.info(f'Registering {hotkey} for action {option} ...')

        # Create profiles hot keys controls
        for profile_key, profile_data in config.changer.options:

            profile = Namespace({
                'card_profile': None,
                'source': '',
                'sink': '',
            })
            profile.update(profile_data)

            changer = Changer(
                client,
                card_profile=profile.card_profile,
                source=profile.source,
                sink=profile.sink,
            )
            self._changers[profile_key] = changer

            hotkey = profile_data.get('hotkey')
            if hotkey:
                self._hotkeys[hotkey] = self.create_changer_activate(
                    hotkey, changer, profile_key,
                )
                log.info(f'Registering {hotkey} for profile {profile_key} ...')

        # Create cycle for changing
        self._cycle = cycle(self._changers)

    def play(self, action):
        """
        Play the sound of the given action.

        This assumes that the file exists in package data.

        Will only play the sound if daemon sounds are enabled.
        """
        if not self.sounds:
            return

        sound = resource_filename(
            __package__,
            f'data/sounds/{action}d.wav',
        )
        play_sound(sound)

    def create_global_activate(self, hotkey, option):
        """
        Create a closure to bind a hotkey with an action callback.
        """
        def on_activate():
            log.info(f'Received {hotkey}. Activating action {option} ...')
            callback = f'on_activate_{option.replace("hotkey_", "", 1)}'

            try:
                getattr(self, callback)()
            except Exception:
                log.exception(f'Failed to execute {callback!r}')

        return on_activate

    def create_changer_activate(self, hotkey, changer, profile_key):
        """
        Create a closure to bind a hotkey with a particular audio profile.
        """

        def on_activate():
            log.info(
                f'Received {hotkey}. Changing profile to {profile_key!r} ...'
            )

            try:
                changer.change()
                self.play('change')
            except Exception:
                log.exception(f'Failed to change to profile {profile_key!r}')

        return on_activate

    def on_activate_mute(self):
        self._muter.mute()
        self.play('mute')

    def on_activate_unmute(self):
        self._muter.unmute()
        self.play('unmute')

    def on_activate_mute_toggle(self):
        if self._muter.is_muted():
            self.on_activate_unmute()
            return
        self.on_activate_mute()

    def on_activate_change_cycle(self):
        profile_key = next(self._cycle)
        changer = self._changers[profile_key]

        log.info(f'Changing to profile {profile_key!r}')

        try:
            changer.change()
            self.play('change')
        except Exception:
            log.exception(f'Failed to change to profile {profile_key!r}')

    def run(self):
        """
        Run the Muttr daemon.
        """
        with GlobalHotKeys(self._hotkeys) as h:
            h.join()


__all__ = [
    'Daemon',
]
