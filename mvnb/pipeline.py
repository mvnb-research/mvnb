from asyncio import Queue, create_task


class Pipeline(object):
    def __init__(self, on_receive):
        self._queue = Queue()
        self._on_receive = on_receive

    def start(self):
        return create_task(self._watch())

    async def wait(self):
        pass

    async def put(self, msg, *args):
        await self._queue.put((msg, args))

    async def _watch(self):
        while True:
            msg, args = await self._queue.get()
            await self._on_receive(msg, *args)
