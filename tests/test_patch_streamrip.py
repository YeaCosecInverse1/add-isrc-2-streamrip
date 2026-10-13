import unittest

from scripts.patch_streamrip import (
    patch_album_batching,
    patch_header_limit,
    patch_playlist_batching,
)


class HeaderLimitPatchTests(unittest.TestCase):
    def test_header_limit_is_added_before_package_imports(self):
        source = "from . import converter, db, exceptions, media, metadata\n"
        patched, changed = patch_header_limit(source)

        self.assertTrue(changed)
        self.assertIn(
            "http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)",
            patched,
        )
        self.assertLess(patched.index("import http.client"), patched.index("from . import"))

    def test_header_limit_patch_is_idempotent(self):
        source = (
            "import http.client\n"
            "http.client._MAXHEADERS = max(http.client._MAXHEADERS, 1000)\n"
        )
        patched, changed = patch_header_limit(source)

        self.assertFalse(changed)
        self.assertEqual(source, patched)


class AlbumBatchPatchTests(unittest.TestCase):
    def test_album_download_is_replaced_and_postprocess_is_preserved(self):
        source = (
            "class Album:\n"
            "    async def download(self):\n"
            "        results = await asyncio.gather(*self.tracks)\n"
            "        for result in results:\n"
            "            pass\n"
            "\n"
            "    async def postprocess(self):\n"
            "        preserve_this_method()\n"
        )
        patched, changed = patch_album_batching(source)

        self.assertTrue(changed)
        self.assertIn('os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10")', patched)
        self.assertIn("for start in range(0, len(self.tracks), batch_size):", patched)
        self.assertIn("preserve_this_method()", patched)

    def test_album_batch_patch_is_idempotent(self):
        source = (
            "class Album:\n"
            "    async def download(self):\n"
            '        batch_size = int(os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10"))\n'
            "        # Album track processing error\n"
            "\n"
            "    async def postprocess(self):\n"
            "        pass\n"
        )
        patched, changed = patch_album_batching(source)

        self.assertFalse(changed)
        self.assertEqual(source, patched)


class PlaylistBatchPatchTests(unittest.TestCase):
    def test_playlist_batch_size_uses_shared_environment_setting(self):
        source = (
            "class Playlist:\n"
            "    async def download(self):\n"
            "        track_resolve_chunk_size = 20\n"
        )
        patched, changed = patch_playlist_batching(source)

        self.assertTrue(changed)
        self.assertIn('os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10")', patched)
        self.assertNotIn("track_resolve_chunk_size = 20", patched)

    def test_playlist_batch_patch_is_idempotent(self):
        source = (
            "track_resolve_chunk_size = int(\n"
            '    os.environ.get("STREAMRIP_TRACK_BATCH_SIZE", "10")\n'
            ")\n"
        )
        patched, changed = patch_playlist_batching(source)

        self.assertFalse(changed)
        self.assertEqual(source, patched)


if __name__ == "__main__":
    unittest.main()
