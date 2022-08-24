from asyncio import Queue as Queue_
from asyncio import create_task


class Queue(object):
    def __init__(self, func):
        self._queue = Queue_()
        self._func = func

    def start(self):
        return create_task(self._watch())

    async def put(self, message, *args):
        await self._queue.put((message, args))

    async def _watch(self):
        while True:
            message, args = await self._queue.get()
            await self._func(message, *args)
