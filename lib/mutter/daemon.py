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

from logging import getLogger

from objns import Namespace
from pynput.keyboard import GlobalHotKeys
from pkg_resources import resource_filename

from .muter import Muter
from .changer import Changer
from .sound import play_sound


log = getLogger(__name__)


class Daemon:

    def __init__(self, client, config, sounds):
        self.client = client
        self.config = config
        self.sounds = sounds

        self._muter = Muter(client, sources=config.muter.sources)
        self._changers = {}

        self._hotkeys = {}

        # Create global hot keys controls
        def create_global_activate(hotkey, option):
            def on_activate():
                log.info(f'Received {hotkey}. Activating action {option} ...')
                getattr(self, f'on_activate_{option}')()
            return on_activate

        for option in [
            'hotkey_mute',
            'hotkey_unmute',
            'hotkey_mute_toggle',
            'hotkey_change_cycle',
        ]:
            hotkey = config.daemon[option]
            if not hotkey:
                continue

            self._hotkeys[hotkey] = create_global_activate(hotkey, option)
            log.info(f'Registering {hotkey} for action {option} ...')

        # Create profiles hot keys controls
        def create_changer_activate(hotkey, changer, profile_key):
            def on_activate():
                log.info(
                    f'Received {hotkey}. Changing profile to {profile_key} ...'
                )
                changer.change()
            return on_activate

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
                self._hotkeys[hotkey] = create_changer_activate(
                    hotkey, changer, profile_key,
                )
                log.info(f'Registering {hotkey} for profile {profile_key} ...')

    def _play(self, action):
        if not self.sounds:
            return

        sound = resource_filename(
            __package__,
            f'data/sounds/{action}d.wav',
        )
        play_sound(sound)

    def on_activate_mute(self):
        self._muter.mute()
        self._play('mute')

    def on_activate_unmute(self):
        self._muter.unmute()
        self._play('unmute')

    def on_activate_mute_toggle(self):
        log.error(f'Unimplemented action mute_togle')

    def on_activate_change_cycle(self):
        log.error(f'Unimplemented action change_cycle')

    def run(self):
        with GlobalHotKeys(self._hotkeys) as h:
            h.join()


__all__ = [
    'Daemon',
]
