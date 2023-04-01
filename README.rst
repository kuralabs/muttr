=====
Muttr
=====

.. image:: https://img.shields.io/pypi/v/muttr
   :target: https://pypi.org/project/muttr/
   :alt: PyPI

.. image:: https://img.shields.io/github/license/kuralabs/muttr
   :target: https://choosealicense.com/licenses/apache-2.0/
   :alt: License

*Mute all inputs, or change audio outputs and inputs easily.*

.. image:: ./muttr.png
   :height: 250px

So, you're in a meeting a need to mute yourself (all microphones!),
independently of the application you're running? Done.

You're done with your meeting, you put your headset down and want to listen to
music in a different audio output? Done.

Your colleague said, hey, can we do a quick meeting? Angrily, you pause your
music and grab your headset. Do I need to change the audio input and output
back to my headset? Yes? Done.

**So, what's Muttr?**

Muttr is a tool specially made for COVID-19 pandemic working from home people.

It allows to:

- Mute all sources (microphones) at the same time, in case the application is
  getting audio from a different source of the one you think its on.

  *Am I muted? Am I muted? Yes, you are!*

- To mute independently of the application you're running (Slack, Zoom, Teams)
  because it mutes the sound server from the operating system (PulseAudio).

  *What was the hotkey for Slack? Oh wait that's the hotkey for Teams! Where*
  *is that damn mute button and why it is so small and hidden and dark?*

- To change between audio profiles, for example, to quickly change to your
  headset before a meeting, and then change back to your speakers to listen
  music.

  *Yay meeting is no more, music fun times, oh wait forget about it.*


Muttr uses PulseAudio API to do all of this, so it is supported in operating
systems that use PulseAudio to control the audio devices. For example, Ubuntu,
and many other Linux based operating systems.

With Muttr you can configure audio profiles, that is, what audio devices,
their inputs and outputs (sources and sinks, in PulseAudio terminology) you
want to use at a determined point in time.

You can mute, unmute, or swap between those audio profiles using the CLI. Or
you can assign a key combination, start the Muttr daemon and perform those
actions using your keyboard. This is great when using macropads!


Install
=======

.. code-block:: sh

    $ sudo pip3 install muttr
    $ muttr --version


Getting Started
===============

Mute and unmute
---------------

::

    $ muttr mute
    $ muttr unmute

The above will mute and unmute all audio sources in the system.

If for any reason there is the need to restrict the audio sources to mute the
following configuration entry may be used:

::

    [muttr.muter]
    sources = ["first_source", "second_source"]

Create a ``config.toml`` with the above entry and run Muttr with:

::

    $ muttr -c config.toml mute
    $ muttr -c config.toml unmute

Use the following command to identify which sources are available in your
system:

::

    $ muttr show


Create and change audio profiles
--------------------------------

First, connect all your devices (Bluetooth headsets, for example), and run:

::

    $ muttr show

A complete tree of your audio system will print.

Create a file ``config.toml`` and fill the profiles you need like this:

::

    [muttr.changer.options.meeting]
    card_profile = [
        "bluez_card.20_74_CF_92_CD_06",
        "Headset Head Unit (HSP/HFP)",
    ]
    source = "OpenComm by Shokz"
    sink = "OpenComm by Shokz"

    [muttr.changer.options.music]
    card_profile = [
        "bluez_card.20_74_CF_92_CD_06",
        "Headset Head Unit (HSP/HFP)",
    ]
    sink = "M-Track 2X2M Digital Stereo (IEC958)"

    [muttr.changer.options.game]
    source = "SteelSeries Arctis 7 Analog Mono"
    sink = "SteelSeries Arctis 7 Analog Stereo"


In this example, the system will have 3 profiles:

#. One for meetings, using a lightweight Bluetooth bone conductor headset.
   Not the best sound, but is good for voices and is the most comfortable for
   those long meetings.
#. One for listening music, using an external interface connected to some
   great monitor speakers.
#. One for gaming, a large over-ear headphones, awesome sound.
   Perfect for immersive experiences.

Once ready, change between audio profiles using:

::

    $ muttr -c config.toml change music
    $ muttr -c config.toml change meeting
    $ muttr -c config.toml change game

As noted, at least a sink or a source needs to be declared. In many situations
there may be the need to change the profile the card associated with the source
or sink is using. In those situations, use the ``card_profile`` and specify
which card and card profile to use when changing to that audio profile.


Enable system wide mode and hotkeys
-----------------------------------

To enable kotkeys to change mute/unmute and change between audio profiles run
Muttr as a daemon:

::

    $ muttr -c config.toml daemon

By default, the following hotkeys are supported:

::

    [muttr.daemon]
    hotkey_mute = "<ctrl>+<alt>+m"
    hotkey_unmute = "<ctrl>+<alt>+u"
    hotkey_mute_toggle = "<cmd_l>+<alt>+m"
    hotkey_change_cycle = "<cmd_l>+<alt>+c"

:hotkey_mute: Mute all sources.
:hotkey_unmute: Unmute all sources.
:hotkey_mute_toggle: Toggle between mute and unmute all sources.
:hotkey_change_cycle: Change / cycle between all configured audio profiles.

The hotkeys can be changed in your ``config.toml`` using the above snippet.
Set to empty string to disable the hotkey.

To enable hotkeys to change to specific audio profiles, set the ``hotkey``
value for the audio profile in the configuration file.

Using the previous example:

::

    [muttr.changer.options.music]
    hotkey = "<cmd_l>+<alt>+1"
    sink = "M-Track 2X2M Digital Stereo (IEC958)"

    [muttr.changer.options.meeting]
    hotkey = "<cmd_l>+<alt>+2"
    card_profile = [
        "bluez_card.20_74_CF_92_CD_06",
        "Headset Head Unit (HSP/HFP)",
    ]
    source = "OpenComm by Shokz"
    sink = "OpenComm by Shokz"

    [muttr.changer.options.game]
    hotkey = "<cmd_l>+<alt>+3"
    source = "SteelSeries Arctis 7 Analog Mono"
    sink = "SteelSeries Arctis 7 Analog Stereo"

With the above configuration the hotkeys ``CMD+ALT+1`` can be used to change to
the ``music`` audio profile, and so on.


Using system wide configuration files
-------------------------------------

Muttr support the following files for system wide and/or user wide setup:

- ``/etc/muttr/config.toml``
- ``~/.config/muttr/config.toml``

Configuration files will be read in that order and the last will override any
configuration from the previous file. Finally, user configuration files passed
using argument ``-c`` or ``--config`` are read last in the order the user
passed the arguments to the CLI.


Changelog
=========

1.0.0 (2023-04-1)
------------------

New
~~~

- Initial public version.
- Support for muting and unmuting.
- Support for audio profiles, changing and cycling.
- Support for global hotkeys and audio profile specific hotkeys.


0.1.0 (2022-05-18)
------------------

New
~~~

- Development preview.


License
=======

::

   Copyright (C) 2017-2023 KuraLabs S.R.L

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
