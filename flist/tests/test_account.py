import unittest
import asyncio
import flist.api

class TestFListAccount(unittest.TestCase):
    def setUp(self):
        pass

    def test_info_list(self):
        future = asyncio.Future()
        @asyncio.coroutine
        def get_info_list():
            data = yield from flist.api.info_list()
            future.set_result(data)

        asyncio.get_event_loop().run_until_complete(get_info_list())
        assert future.result()['error'] == ""