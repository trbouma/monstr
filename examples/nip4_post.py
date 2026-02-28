import asyncio
import logging
from monstr.client.client import Client, ClientPool
from monstr.encrypt import Keys
from monstr.event.event import Event
from monstr.encrypt import NIP4Encrypt

USE_KEY = Keys('nsec1rc3r6kh5fdfnwrftymys3ug5wvr402uwdgklpp6rtmt7epeackdsdvelye')
# PUB_KEY = "06b7819d7f1c7f5472118266ed7bca8785dceae09e36ea3a4af665c6d1d8327c"



async def do_post(url, text, to_k):
    """
        Example showing how to post a encrypted note (Kind 4) to relay
    """

    my_enc = NIP4Encrypt(USE_KEY)

    async with Client(url) as c:
        n_msg = Event(kind=Event.KIND_ENCRYPT,
                      content=text,
                      pub_key=to_k)

        # returns event we to_p_tag and content encrypted
        n_msg = my_enc.encrypt_event(evt=n_msg,
                                     to_pub_k=to_k)

        n_msg.sign(USE_KEY.private_key_hex())
        c.publish(n_msg)

        # await asyncio.sleep(1)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    url = "wss://relay.nimo.cash"
    to_k = Keys('06b7819d7f1c7f5472118266ed7bca8785dceae09e36ea3a4af665c6d1d8327c')
  

    text = f'Hello partner this is another nip04 encrypted to {to_k}'

    asyncio.run(do_post(url, text, to_k))