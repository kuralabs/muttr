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
Argument management module.
"""

from pathlib import Path
from argparse import ArgumentParser
from logging import (
    ERROR, WARNING, DEBUG, INFO,
    StreamHandler, getLogger, Formatter, basicConfig,
)

from colorlog import ColoredFormatter

from . import __version__


log = getLogger(__name__)


COLOR_FORMAT = (
    '  {thin_white}{asctime}{reset} | '
    '{log_color}{levelname:8}{reset} | '
    '{log_color}{message}{reset}'
)
SIMPLE_FORMAT = (
    '  {asctime} | '
    '{levelname:8} | '
    '{message}'
)
LEVELS = {
    0: ERROR,
    1: WARNING,
    2: INFO,
    3: DEBUG,
}


class InvalidArguments(Exception):
    """
    Typed exception that allows to fail in argument parsing and verification
    without quitting the process.
    """
    pass


def validate_args(args):
    """
    Validate that arguments are valid.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`

    :return: The validated namespace.
    :rtype: :py:class:`argparse.Namespace`
    """

    # Setup logging
    level = LEVELS.get(args.verbosity, DEBUG)

    if not args.colorize:
        formatter = Formatter(
            fmt=SIMPLE_FORMAT, style='{'
        )
    else:
        formatter = ColoredFormatter(
            fmt=COLOR_FORMAT, style='{'
        )

    handler = StreamHandler()
    handler.setFormatter(formatter)

    basicConfig(
        handlers=[handler],
        level=level,
    )

    log.debug('Arguments:\n{}'.format(args))

    # Check if files and directories exists
    for human, argsattr, checker in [
        ('configurations', 'configs', lambda path: path.is_file()),
    ]:
        assert hasattr(args, argsattr)
        files = getattr(args, argsattr)
        if not files:
            continue

        files = [
            Path(file)
            for file in files
        ]

        # Check if exists
        missing = [
            file
            for file in files
            if not file.exists()
        ]
        if missing:
            raise InvalidArguments(
                'No such {}: {}'.format(
                    human,
                    ', '.join(map(str, missing)),
                )
            )

        # Check if valid
        invalid = [
            file
            for file in files
            if not checker(file)
        ]
        if invalid:
            raise InvalidArguments(
                'Invalid {} {}'.format(
                    human,
                    ', '.join(map(str, invalid)),
                )
            )

        files = [
            file.resolve()
            for file in files
        ]

        setattr(args, argsattr, files)

    return args


def parse_args(argv=None):
    """
    Argument parsing routine.

    :param argv: A list of argument strings.
    :type argv: list

    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """

    parser = ArgumentParser(
        description=(
            'Muttr - '
            'Mute all inputs, or change audio outputs and inputs easily.'
        )
    )

    # Standard options
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        dest='verbosity',
        default=0,
        help='Increase verbosity level',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=__version__,
    )
    parser.add_argument(
        '--no-color',
        action='store_false',
        dest='colorize',
        help='Do not colorize the log output'
    )
    parser.add_argument(
        '--no-sounds',
        action='store_false',
        dest='sounds',
        help='Do not play sounds on actions'
    )

    # Configuration
    parser.add_argument(
        '-c', '--config',
        action='append',
        dest='configs',
        default=[],
        help=(
            'Configuration files. Must be a .toml file.'
            'All files are parsed and merged left to right.'
        ),
    )

    subparsers = parser.add_subparsers(dest='command')

    # Mute command
    cmd_mute = subparsers.add_parser(  # noqa
        'mute',
        help='Mute all (or configured) audio inputs'
    )

    # Unmute command
    cmd_unmute = subparsers.add_parser(  # noqa
        'unmute',
        help='Unmute all (or configured) audio inputs'
    )

    # Change command
    cmd_change = subparsers.add_parser(  # noqa
        'change',
        help='Change profile, inputs and outputs'
    )
    cmd_change.add_argument(
        'name',
        help='Audio profile name to change to',
    )

    # Show command
    cmd_show = subparsers.add_parser(  # noqa
        'show',
        help=(
            'Show all cards, profiles, sinks and sources '
            'found in the PulseAudio server'
        ),
    )

    # Daemon command
    cmd_daemon = subparsers.add_parser(  # noqa
        'daemon',
        help='Launch the Muttr daemon'
    )

    # Parse and validate arguments
    args = parser.parse_args(argv)

    try:
        args = validate_args(args)
    except InvalidArguments as e:
        log.critical(e)
        raise e

    return args


__all__ = [
    'parse_args',
]
