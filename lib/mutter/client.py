"""
Change the system default source and/or sink using PulseAudio.
"""

from logging import getLogger

from pulsectl import Pulse


log = getLogger(__name__)


class Client:

    def __init__(self, **kwargs):
        self.pulse = Pulse(**kwargs)
        self.log_system()

    def log_system(self):

        info = self.pulse.server_info()
        log.info(
            f'Connected to PulseAudio Server '
            f'{info.server_name!r} v{info.server_version} as '
            f'{info.user_name}@{info.host_name}'
        )

        log.info('Sources found:')
        for source in self.find_all_sources():
            log.info(f'    -> {source.description}')

            profiles = sorted(
                self.pulse.card_info(source.card).profile_list,
                key=lambda profile: profile.description,
            )
            if len(profiles) > 1:
                log.info(f'         Profiles:')
                for profile in profiles:
                    log.info(f'         -> {profile.description}')

        log.info('Sinks found:')
        for source in self.find_all_sinks():
            log.info(f'    -> {source.description}')

    def find_all_sources(self):
        """
        Return the list of sources found in the system.
        """
        return sorted(
            (
                source
                for source in self.pulse.source_list()
                if source.monitor_of_sink_name is None
            ),
            key=lambda s: s.description,
        )

    def find_all_sinks(self):
        """
        Return the list of sinks found in the system.
        """
        return sorted(
            self.pulse.sink_list(),
            key=lambda s: s.description,
        )


__all__ = [
    'Client',
]
