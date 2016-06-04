import unittest
import asyncio
from flist.aiter_provider import Provider


class TestProvider(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.provider = Provider()

    @staticmethod
    async def event_runner(provider, future):
        results = []
        async for thing in provider:
            if thing:
                results.append(thing)

        future.set_result(results)

    def test_provider_returns_values(self):
        self.provider.put_item("Something")
        self.provider.put_item(False)
        self.provider.put_item(42)
        self.provider.close()

        future = asyncio.Future()
        self.loop.run_until_complete(self.event_runner(self.provider, future))

        self.assertTrue(future.done())
        self.assertEqual(["Something", 42], future.result())

    def test_closed_provider_stops_attached_methods(self):
        self.provider.close()
        future = asyncio.Future()
        self.loop.run_until_complete(self.event_runner(self.provider, future))
        self.assertTrue(future.done())
        self.assertEqual([], future.result())
