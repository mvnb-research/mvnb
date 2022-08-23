from asyncio import Queue as Queue_
from asyncio import create_task


class Queue(object):
    def __init__(self, func):
        self._queue = Queue_()
        self._func = func

    def start(self):
        return create_task(self._watch())

    async def put(self, msg, *args):
        await self._queue.put((msg, args))

    async def _watch(self):
        while True:
            msg, args = await self._queue.get()
            await self._func(msg, *args)
