import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from spotify_auth import clear_stored_spotify_auth, get_spotify_client


class SpotifyAuthTests(unittest.TestCase):
    def test_clear_stored_spotify_auth_removes_env_and_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                Path('.env').write_text('REFRESH_TOKEN=old-token\n', encoding='utf-8')
                Path('.cache').write_text('cached-token', encoding='utf-8')

                clear_stored_spotify_auth()

                self.assertFalse(Path('.cache').exists())
                self.assertFalse(Path('.env').exists())
            finally:
                os.chdir(old_cwd)

    def test_get_spotify_client_raises_clear_error_for_invalid_grant(self):
        class FakeAuthManager:
            def refresh_access_token(self, refresh_token):
                raise Exception('invalid_grant')

        with patch('spotify_auth.build_spotify_auth_manager', return_value=FakeAuthManager()):
            with self.assertRaisesRegex(RuntimeError, 're-authorize'):
                get_spotify_client(scope='user-read-recently-played', refresh_token='old-token')


if __name__ == '__main__':
    unittest.main()
