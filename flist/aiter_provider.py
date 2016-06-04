import collections
import asyncio


class Provider:
    def __init__(self):
        self.buffer = collections.deque()
        self._add_new_future()

    def _add_new_future(self):
        self.current_value = asyncio.Future()
        self.buffer.append(self.current_value)

    async def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.buffer.popleft()

    def put_item(self, item):
        self.current_value.set_result(item)
        self._add_new_future()

    def close(self):
        self.current_value.set_exception(StopAsyncIteration)
