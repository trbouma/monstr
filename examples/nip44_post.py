import asyncio
import logging
from monstr.client.client import Client, ClientPool
from monstr.encrypt import Keys
from monstr.event.event import Event
from monstr.encrypt import NIP44Encrypt

async def do_post(url, text, to_k):
    """
        Example showing how to post a encrypted note (Kind 4) to relay
    """
    # rnd generate some keys we sending as
    n_keys = Keys()
    my_enc = NIP44Encrypt(n_keys)

    async with Client(url) as c:
        n_msg = Event(kind=Event.KIND_TEXT_NOTE,
                      content=text,
                      pub_key=n_keys.public_key_hex())

        # returns event we to_p_tag and content encrypted
        n_msg = my_enc.encrypt_event(evt=n_msg,
                                     to_pub_k=to_k)

        n_msg.sign(n_keys.private_key_hex())
        c.publish(n_msg)
        # await asyncio.sleep(1)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    url = "wss://relay.nimo.cash"
    to_k = Keys("06b7819d7f1c7f5472118266ed7bca8785dceae09e36ea3a4af665c6d1d8327c")
   
    text = f'hello this is nip44 encrypted to: {to_k.public_key_hex}'

    asyncio.run(do_post(url, text, to_k))