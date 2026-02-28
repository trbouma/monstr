import asyncio
import logging
from monstr.client.client import Client
import signal
from monstr.event.event import Event
from monstr.util import util_funcs

tail = util_funcs.str_tails


async def listen_notes(url):
    run = True

    # so we get a clean exit on ctrl-c
    def sigint_handler(signal, frame):
        nonlocal run
        run = False
    signal.signal(signal.SIGINT, sigint_handler)

    # just use func, you can also use a class that has a do_event
    # with this method sig, e.g. extend monstr.client.EventHandler
    def my_handler(the_client: Client, sub_id: str, evt: Event):
        print(evt.pub_key, evt.created_at, tail(evt.id), tail(evt.content, 30))

    def on_connect(the_client: Client):
        # sub in onconnect so will re-sub if disconnect
        the_client.subscribe(handlers=my_handler,
                             filters={
                                 
                                 'limit': 100,
                                 'kinds': [4],
                                 'tags': [["p", "3a402df8f27653eb2ad7806cb0f8e8d2445d917f892cb4a835bbea1c040abe39"]]
                             })

    # create the client and start it running
    c = Client(url, on_connect=on_connect)
    asyncio.create_task(c.run())
    await c.wait_connect()

    while run:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    url = "wss://relay.nimo.cash"

    asyncio.run(listen_notes(url))