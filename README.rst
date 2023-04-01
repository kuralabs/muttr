======
Mutter
======

Mute all inputs, or change audio outputs and inputs easily.

So, you're in a meeting a need to mute yourself (all microphones!),
independently of the application you're running? Done.

You're done with your meeting, you put your headset down and want to listen to
music in a different audio output? Done.

Your collegue said, hey, can we do a quick meeting? Angrily, you pause your
music and grab your headset. Do I need to change the audio input and output
back to my headset? Yes? Done.

So, what's Mutter?

Mutter is a tool specially made for COVID-19 pandemic working from home people.

It allows to:

- Mute all sources (microphones) at the same time, in case the application is
  getting audio from a different source of the one you think its on.

  > Am I muted? Am I muted? Yes, you are!

- To mute independently of the application you're running (Slack, Zoom, Teams)
  because it mutes the sound server from the operating system (PulseAudio).

  > What was the hotkey for Slack? Oh wait that's the hotkey for Teams! Where
  > is that damn mute button and why it is so small and hidden and dark?

- To change between audio profiles, for example, to quickly change to your
  headset before a meeting, and then change back to your speakers to listen
  music.

  > Yay meeting is no more, music fun times, oh wait forget about it.

.. image:: https://img.shields.io/pypi/v/mutter
   :target: https://pypi.org/project/mutter/
   :alt: PyPI

.. image:: https://img.shields.io/github/license/kuralabs/mutter
   :target: https://choosealicense.com/licenses/apache-2.0/
   :alt: License


Mutter uses PulseAudio API to do all of this, so it is supported in operating
systems that use PulseAudio to control the audio devices. For example, Ubuntu,
and many other Linux based operating systems.

With Mutter you can configure audio profiles, that is, what audio devices,
their inputs and outputs (sources and sinks, in PulseAudio terminology) you
want to use at a determined point in time.

You can mute, unmute, or swap between those audio profiles using the CLI. Or
you can assign a key combination, start the Mutter daemon and perform those
actions using your keyboard. This is great when using macropads!


Install
=======

.. code-block:: sh

    $ sudo pip3 install mutter
    $ mutter --version


Create and change audio profiles
================================

First, connect all your devices (Bluetooth headsets, for example), and run:

::

    $ mutter show

A complete tree of your audio system will print.

Create a file `config.toml` and fill the profiles you need like this:

::

    [mutter.changer.options.meeting]
    card_profile = [
        "bluez_card.20_74_CF_92_CD_06",
        "Headset Head Unit (HSP/HFP)",
    ]
    source = "OpenComm by Shokz"
    sink = "OpenComm by Shokz"

    [mutter.changer.options.music]
    card_profile = [
        "bluez_card.20_74_CF_92_CD_06",
        "Headset Head Unit (HSP/HFP)",
    ]
    sink = "M-Track 2X2M Digital Stereo (IEC958)"

    [mutter.changer.options.game]
    source = "SteelSeries Arctis 7 Analog Mono"
    sink = "SteelSeries Arctis 7 Analog Stereo"


In this example, the system will have 3 profiles:

#. One for meetings, using a lightweight Bluetooth bone conductor headset.
   Not the best sound, but is good for voices and is the most comfortable for
   those long meetings.
#. One for gaming, a large over-ear headphones, awesome sound.
   Perfect for immersive experiences.
#. One for listening music, using an external interface connected to some
   great monitor speakers.

Once ready, change between audio profiles using:

::

    $ mutter change music
    $ mutter change meeting
    $ mutter change game


Changelog
=========

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
