import collections
import asyncio


class Provider:
    def __init__(self, **kwargs):
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


class CountProvider(Provider):
    def __init__(self, *, count=1, **kwargs):
        super().__init__(**kwargs)
        self.count = count

    def put_item(self, item):
        super().put_item(item)
        self.count -= 1
        if self.count == 0:
            self.close()


class CloserProvider(Provider):
    def __init__(self, *, closer, **kwargs):
        super().__init__(**kwargs)
        self._closer = closer

    def close(self):
        super().close()
        self._closer(self)


class CountCloserProvider(CloserProvider, CountProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
