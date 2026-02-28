# -*- coding: utf-8 -*-
"""service.chronicle.scrobbler — Background service entry point.

Kodi starts this automatically when the user logs in (extension point
xbmc.service, start="login").  It instantiates ChronicleMonitor and
blocks until Kodi signals an abort.
"""

from lib.monitor import ChronicleMonitor
from lib.logger import Logger

log = Logger('service')


def main():
    log.info('Chronicle Scrobbler v1.0.0 starting')
    monitor = ChronicleMonitor()
    monitor.run()
    log.info('Chronicle Scrobbler stopped')


if __name__ == '__main__':
    main()
