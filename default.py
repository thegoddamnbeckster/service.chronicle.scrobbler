# -*- coding: utf-8 -*-
"""service.chronicle.scrobbler — Script entry point.

Shown when the user opens the addon from the Kodi add-on browser.
Presents a simple action menu:
  • Reset TV Show Progress
  • Reset Movie Progress
  • Test Connection
  • Open Settings
"""

import xbmcgui
import xbmcaddon

from lib.logger import Logger
from lib.chronicle_client import ChronicleClient
from lib.reset_manager import ResetManager

ADDON = xbmcaddon.Addon()
log   = Logger('default')


def show_menu():
    """Display the main action menu."""
    options = [
        ADDON.getLocalizedString(32010),  # Reset TV Show Progress
        ADDON.getLocalizedString(32011),  # Reset Movie Progress
        ADDON.getLocalizedString(32012),  # Test Connection
        ADDON.getLocalizedString(32013),  # Open Settings
    ]

    dialog = xbmcgui.Dialog()
    choice = dialog.select(ADDON.getLocalizedString(32000), options)

    if choice == 0:
        ResetManager().prompt_reset_tvshow()
    elif choice == 1:
        ResetManager().prompt_reset_movie()
    elif choice == 2:
        _test_connection()
    elif choice == 3:
        ADDON.openSettings()


def _test_connection():
    """Test connectivity to Chronicle and display a result dialog."""
    client  = ChronicleClient()
    dialog  = xbmcgui.Dialog()
    ok, msg = client.test_connection()

    if ok:
        dialog.ok(
            ADDON.getLocalizedString(32012),
            ADDON.getLocalizedString(32020),   # Connection successful!
        )
    else:
        dialog.ok(
            ADDON.getLocalizedString(32012),
            '{0}\n{1}'.format(ADDON.getLocalizedString(32021), msg),   # Connection failed: <msg>
        )


if __name__ == '__main__':
    show_menu()
