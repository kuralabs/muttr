"""
[Un]Mute all sound sources using PulseAudio.
"""

from logging import getLogger


log = getLogger(__name__)


class Muter:

    def __init__(self, client, sources=None):
        self.client = client
        self.sources = sources

    def find(self):

        if not self.sources:
            return self.client.find_all_sources()

        return [
            source
            for source in self.client.find_all_sources()
            if source.description in self.sources
        ]

    def is_muted(self):
        return all(
            bool(source.mute)
            for source in self.find()
        )

    def mute(self):
        for source in self.find():
            self.client.pulse.mute(source, mute=True)
            self.client.pulse.volume_set_all_chans(source, 0.0)

    def unmute(self):
        for source in self.find():
            self.client.pulse.mute(source, mute=False)
            self.client.pulse.volume_set_all_chans(source, 1.0)


__all__ = [
    'Muter',
]
