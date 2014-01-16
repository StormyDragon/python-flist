import unittest
import asyncio
import flist.api

class TestFListAPI(unittest.TestCase):
    def setUp(self):
        pass

    def test_info_list(self):
        future = asyncio.Future()
        @asyncio.coroutine
        def get_info_list():
            data = yield from flist.api.info_list()
            future.set_result(data)

        asyncio.get_event_loop().run_until_complete(get_info_list())
        result = future.result()
        self.assertIsInstance(result, dict, "The result must be a dict.")
        self.assertTrue('error' in result, "The dict must contain a key named 'error'.")
        self.assertIsInstance(result['error'], str, "The dict must contain a string on it's error key.")