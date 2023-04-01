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
Argument management module.
"""

from logging import getLogger

from objns import Namespace
from pulsectl import PulseIndexError
from pkg_resources import resource_string, resource_filename

try:
    # Standard library, available in Python 3.11
    from tomllib import loads
except ImportError:
    from tomli import loads

from .muter import Muter
from .client import Client
from .daemon import Daemon
from .changer import Changer
from .sound import play_sound
from .args import InvalidArguments, parse_args


log = getLogger(__name__)


def load_config(configs):
    """
    Load application default configuration and apply overrides from the the
    given configurations files, in the order given.

    :param list configs: List of paths to configuration files (TOML).

    :return: The final, overriden and merged configuration.
    :rtype: dict
    """
    config = Namespace(loads(
        resource_string(
            __package__, 'data/config.toml'
        ).decode(encoding='utf-8')
    )).muttr

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

    # Change command
    if args.command == 'change':
        profile = Namespace({
            'card_profile': None,
            'source': '',
            'sink': '',
        })

        try:
            profile.update(
                getattr(config.changer.options, args.name)
            )
        except AttributeError:
            log.error(
                f'Unknown profile {args.name!r}. '
                f'Please review your configuration files.'
            )
            return 1

        changer = Changer(
            client,
            card_profile=profile.card_profile,
            source=profile.source,
            sink=profile.sink,
        )

        try:
            changer.change()
        except PulseIndexError as e:
            log.error(
                f'Unable to change to the selected profile {args.name!r}. '
                f'Card, source or sink couldn\'t be found: {e}'
            )
            return 1

        log.info(
            'PulseAudio was successfully changed to:'
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

    # Mute/unmute command
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

    # Show command
    if args.command == 'show':
        client.show_system(logger=print)
        return 0

    # Daemon command
    if args.command == 'daemon':
        client.show_system(logger=print)
        daemon = Daemon(client, config, args.sounds)
        daemon.run()
        return 0

    return 1


if __name__ == '__main__':
    exit(main())


__all__ = []
