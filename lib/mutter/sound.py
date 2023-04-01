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
Utility module to play sounds.
"""

from shutil import which
from pathlib import Path
from subprocess import run
from logging import getLogger


log = getLogger(__name__)


def _play_gstreamer(sound):
    """
    Play a sound using GStreamer.

    Inspired by:

        https://github.com/TaylorSMarks/playsound/blob/master/playsound.py

    :param str sound: URI to sound.
     Schemas https://, http:// and file:// are supported.
    """

    # Initialize GStreamer
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)

    # Prepare player
    player = Gst.ElementFactory.make('playbin', 'player')
    player.props.uri = sound

    # Start playing the sound
    result = player.set_state(Gst.State.PLAYING)
    if result != Gst.StateChangeReturn.ASYNC:
        raise RuntimeError(
            'Failed to start playing the audio: {}'.format(repr(result))
        )

    # Wait until end or error
    bus = player.get_bus()
    message = bus.poll(
        Gst.MessageType.EOS | Gst.MessageType.ERROR,
        Gst.CLOCK_TIME_NONE,
    )
    player.set_state(Gst.State.NULL)

    if message.type == Gst.MessageType.ERROR:
        raise RuntimeError(message.parse_error()[1])


def _play_aplay(sound):
    """
    Play a sound using system's aplay executable.

    :param str sound: Path to local sound available in current system.
    """

    sound = Path(sound)

    if not sound.is_file():
        raise FileNotFoundError('No such file {}'.format(str(sound)))

    aplay = which('aplay')
    if not aplay:
        raise RuntimeError('aplay isn\'t available')

    run([aplay, '-q', str(sound)])


def play_sound(sound):
    """
    Play the given local filesystem sound.

    :param str sound: Path object or string to a sound in the local file
     system.
    """
    sound = Path(sound).resolve(strict=True)

    try:
        _play_gstreamer(f'file://{sound}')
        return
    except Exception:
        log.exception(f'Failed to play sound {sound!r} using GStreamer')

    try:
        _play_aplay(sound)
    except Exception as e:
        log.exception(f'Failed to play sound {sound!r} using aplay')
        raise e


__all__ = [
    'play_sound',
]
