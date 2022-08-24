from asyncio import Event

from pytest import mark

from mvnb.queue import Queue


@mark.asyncio
async def test_queue():
    class Receiver(object):
        def __init__(self):
            self.items = []
            self.event = Event()

        async def __call__(self, msg, *args):
            self.items.append((msg, args))
            self.event.set()

    receiver = Receiver()
    queue = Queue(receiver)
    task = queue.start()
    await queue.put(1, 2, 3)
    await receiver.event.wait()
    assert receiver.items == [(1, (2, 3))]
    task.cancel()
