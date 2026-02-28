import asyncio
import signal
import sys
import datetime
from datetime import timedelta
import logging
from monstr.client.client import Client, ClientPool
from monstr.client.event_handlers import DeduplicateAcceptor
import aioconsole
from monstr.event.event import Event
from monstr.util import util_funcs
from monstr.signing.signing import BasicKeySigner
from monstr.encrypt import NIP4Encrypt, Keys, NIP44Encrypt
from monstr.giftwrap import GiftWrap

tail = util_funcs.str_tails




async def listen_notes():


    AS_K = 'nsec13a77t68puh24wyff9t8a2wr43uulmxtsgyyvxvw66rr9lv2g3nzqdqsp6k'
    TO_K = 'npub1q6mcr8tlr3l4gus3sfnw6772s7zae6hqncmw5wj27ejud5wcxf7q0nx7d5'
    my_k = Keys(AS_K)

    my_gift = GiftWrap(BasicKeySigner(my_k))
    send_k = Keys(pub_k=TO_K)

    print(f'running as npub{tail(my_k.public_key_bech32()[4:])}, messaging npub{tail(send_k.public_key_bech32()[4:])}')

    relays = ['wss://strfry.openbalance.app']
    print("relays", relays)
    

    c = ClientPool(relays)
    
    asyncio.create_task(c.run())
    msg_n = ''
    while msg_n != 'exit':
        msg_n = await aioconsole.ainput('')
        print(msg_n)
        send_evt = Event(content=msg_n,
                            tags=[
                             ['p', send_k.public_key_hex()]
                         ])

        wrapped_evt, trans_k = await my_gift.wrap(send_evt,
                                                  to_pub_k=send_k.public_key_hex())
            # wrapped_evt.sign(self.privkey_hex)
        c.publish(wrapped_evt)
        print("event published")

#####
print("this is main")
asyncio.run(listen_notes())

