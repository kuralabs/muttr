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
Argument management module.
"""

from logging import getLogger

from objns import Namespace
from pkg_resources import resource_string, resource_filename

try:
    # Standard library, available in Python 3.11
    from tomllib import loads
except ImportError:
    from tomli import loads

from .muter import Muter
from .client import Client
from .changer import Changer
from .sound import play_sound
from .args import InvalidArguments, parse_args


log = getLogger(__name__)


def load_config(configs):
    config = Namespace(loads(
        resource_string(
            __package__, 'data/config.toml'
        ).decode(encoding='utf-8')
    )).mutter

    for configfile in configs:
        config.update(loads(
            configfile.read_text(encoding='utf-8')
        ))

    return config


def main():
    # Parse arguments
    try:
        args = parse_args()
    except InvalidArguments:
        return 1

    config = load_config(args.configs)

    client = Client()
    client.log_system()

    # Change command
    if args.command == 'change':
        profile = Namespace({
            'card_profile': None,
            'source': '',
            'sink': '',
        })
        profile.update(
            getattr(config.changer.options, args.name)
        )

        changer = Changer(
            client,
            card_profile=profile.card_profile,
            source=profile.source,
            sink=profile.sink,
        )
        changer.change()

        log.info(
            f'PulseAudio was successfully changed to:'
        )
        if changer.card_profile:
            log.info(
                f'Profile: {changer.card_profile[1]!r} '
                f'(Card: {changer.card_profile[0]!r})'
            )
        if changer.source:
            log.info(
                f'Source: {changer.source!r}'
            )
        if changer.sink:
            log.info(
                f'Sink: {changer.sink!r}'
            )

        return 0

    if args.command in ['mute', 'unmute']:
        muter = Muter(client, sources=config.muter.sources)
        action = getattr(muter, args.command)

        action()

        log.info(f'Successfully {args.command}d the following sources:')
        for source in muter.find():
            log.info(f'    -> {source.description}')

        if args.sounds:
            sound = resource_filename(
                __package__,
                f'data/sounds/{args.command}d.wav',
            )
            play_sound(sound)
        return 0

    return 1


if __name__ == '__main__':
    exit(main())


__all__ = []
