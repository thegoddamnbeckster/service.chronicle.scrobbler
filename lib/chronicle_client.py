# -*- coding: utf-8 -*-
"""HTTP client for the Chronicle REST API.

Uses urllib from the Python standard library — no third-party packages
needed inside Kodi's Python environment.

Authentication: X-Api-Key header (Chronicle scrobbler API key).
"""

import json
import urllib.request
import urllib.error
import xbmcaddon

from lib.logger import Logger

ADDON = xbmcaddon.Addon()
log   = Logger('client')

_USER_AGENT = 'Kodi/Chronicle-Scrobbler/1.0'


class ChronicleClient:
    """Sends scrobble events and health-check requests to a Chronicle server."""

    def __init__(self):
        self._base_url = ADDON.getSetting('chronicle_url').rstrip('/')
        self._api_key  = ADDON.getSetting('api_key')

    def refresh_settings(self):
        """Re-read URL and API key from addon settings.

        Call this after a device-auth flow completes so the client picks up
        the newly saved API key without needing to be reconstructed.
        """
        self._base_url = ADDON.getSetting('chronicle_url').rstrip('/')
        self._api_key  = ADDON.getSetting('api_key')

    # ── public ──────────────────────────────────────────────────────────────────

    def scrobble(self, payload: dict) -> bool:
        """POST /api/v1/scrobble — send a playback progress event.

        Expected payload keys:
            mediaType    (str)   'movie' | 'episode' | 'track'
            title        (str)   Media title
            year         (int)   Release year
            season       (int)   Season number  [episodes only]
            episode      (int)   Episode number [episodes only]
            showTitle    (str)   TV show title  [episodes only]
            progress     (float) 0.0–100.0 — percentage watched
            currentTime  (float) Elapsed time in seconds
            totalTime    (float) Total duration in seconds
            externalIds  (dict)  {'imdb': '...', 'tmdb': '...', 'tvdb': '...'}
            playerName   (str)   'Kodi'

        Returns True on success (HTTP 2xx), False otherwise.
        """
        if not self._base_url or not self._api_key:
            log.warning('Chronicle URL or API key not configured — scrobble skipped')
            return False

        url  = '{0}/api/v1/scrobble'.format(self._base_url)
        data = json.dumps(payload).encode('utf-8')
        req  = self._build_request(url, data=data, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201, 204):
                    log.debug('Scrobble accepted (HTTP {0})'.format(resp.status))
                    return True
                log.warning('Scrobble returned unexpected HTTP {0}'.format(resp.status))
                return False
        except urllib.error.HTTPError as exc:
            log.error('Scrobble HTTP {0}: {1}'.format(exc.code, exc.reason))
            return False
        except Exception as exc:
            log.error('Scrobble failed: {0}'.format(exc))
            return False

    def get_lists(self) -> list:
        """GET /api/v1/lists — return all lists for the authenticated user.

        Returns a list of list-summary dicts (id, name, isOrdered, itemCount,
        description) or an empty list on error.
        """
        if not self._base_url or not self._api_key:
            log.warning('Chronicle URL or API key not configured — get_lists skipped')
            return []

        url = '{0}/api/v1/lists'.format(self._base_url)
        req = self._build_request(url)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                return body.get('data', [])
        except Exception as exc:
            log.error('get_lists failed: {0}'.format(exc))
            return []

    def get_list(self, list_id: int) -> dict:
        """GET /api/v1/lists/{id} — return a single list with all its items.

        Returns the data dict (id, name, isOrdered, items[]) or an empty dict
        on error.
        """
        if not self._base_url or not self._api_key:
            log.warning('Chronicle URL or API key not configured — get_list skipped')
            return {}

        url = '{0}/api/v1/lists/{1}'.format(self._base_url, list_id)
        req = self._build_request(url)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                return body.get('data', {})
        except Exception as exc:
            log.error('get_list({0}) failed: {1}'.format(list_id, exc))
            return {}

    def test_connection(self):
        """GET /api/health — verify connectivity and API key.

        Returns a (success: bool, message: str) tuple.
        """
        if not self._base_url:
            return False, 'Chronicle URL is not configured.'

        url = '{0}/api/health'.format(self._base_url)
        req = self._build_request(url)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True, ''
                return False, 'Unexpected HTTP {0}'.format(resp.status)
        except urllib.error.HTTPError as exc:
            return False, 'HTTP {0}: {1}'.format(exc.code, exc.reason)
        except Exception as exc:
            return False, str(exc)

    # ── private ─────────────────────────────────────────────────────────────────

    def _build_request(self, url: str, data=None, method: str = 'GET') -> urllib.request.Request:
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key':    self._api_key,
            'User-Agent':   _USER_AGENT,
        }
        return urllib.request.Request(url, data=data, headers=headers, method=method)
