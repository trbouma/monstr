import argparse
import asyncio
import hashlib
import logging
from pathlib import Path

from monstr.client.client import ClientPool
from monstr.event.event import Event


DEFAULT_RELAY = "wss://relay.getsafebox.app/"
DEFAULT_TIMEOUT = 10
DEFAULT_LIMIT = 20


def get_args():
    parser = argparse.ArgumentParser(
        prog="query_o_tag.py",
        description="Query a relay for events matching a NIP-01 #o tag value.",
    )
    parser.add_argument(
        "-r",
        "--relay",
        default=DEFAULT_RELAY,
        help=f"comma separated relay URLs to query, default [{DEFAULT_RELAY}]",
    )
    parser.add_argument(
        "-d",
        "--digest",
        default=None,
        help="64-character hex digest to query for",
    )
    parser.add_argument(
        "-f",
        "--digest-file",
        default=None,
        help="path to a file to hash with SHA-256 and use as the #o filter value",
    )
    parser.add_argument(
        "-k",
        "--kinds",
        default=None,
        help="comma separated event kinds to narrow the query",
    )
    parser.add_argument(
        "-a",
        "--authors",
        default=None,
        help="comma separated author pubkeys to narrow the query",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"result limit, default [{DEFAULT_LIMIT}]",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"query timeout in seconds, default [{DEFAULT_TIMEOUT}]",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["heads", "full", "raw", "tags"],
        default="full",
        help="output format",
    )
    parser.add_argument(
        "--ssl-disable-verify",
        action="store_true",
        help="disable SSL certificate verification",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging",
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    if args.digest_file:
        digest_path = Path(args.digest_file).expanduser()
        if not digest_path.is_file():
            raise ValueError(f"digest-file does not exist or is not a file: {digest_path}")

        file_hash = hashlib.sha256()
        with digest_path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                file_hash.update(chunk)
        args.digest = file_hash.hexdigest()

    if not args.digest:
        raise ValueError("you must supply either --digest or --digest-file")

    args.digest = args.digest.lower()
    if len(args.digest) != 64:
        raise ValueError("digest must be exactly 64 hex characters")

    try:
        int(args.digest, 16)
    except ValueError as exc:
        raise ValueError("digest must be valid hex") from exc

    if args.kinds:
        args.kinds = [int(kind.strip()) for kind in args.kinds.split(",") if kind.strip()]

    if args.authors:
        args.authors = [author.strip() for author in args.authors.split(",") if author.strip()]

    return args


def print_event(evt: Event, output: str):
    if output == "raw":
        print(evt.event_data())
        print(evt.tags)
        print(f"content: {evt.content}")
        return

    if output == "tags":
        print(evt)
        print(f"content: {evt.content}")
        for tag in evt.tags:
            print(tag)
        print(f"total {len(evt.tags)}")
        return

    print(evt)
    print(f"content: {evt.content}")
    if output == "full":
        print("-" * 80)
        print(evt.content)
        print()


async def do_query(args):
    ssl = False if args.ssl_disable_verify else None

    query_filter = {
        "#o": [args.digest],
        "limit": args.limit,
    }
    if args.kinds:
        query_filter["kinds"] = args.kinds
    if args.authors:
        query_filter["authors"] = args.authors

    print(f"Relay filter: {query_filter}")
    if args.digest_file:
        print(f"Digest source: sha256({Path(args.digest_file).expanduser()})")

    async with ClientPool(
        args.relay.split(","),
        query_timeout=args.timeout,
        timeout=args.timeout,
        ssl=ssl,
    ) as client:
        events = await client.query(
            query_filter,
            emulate_single=True,
            wait_connect=True,
            timeout=args.timeout,
        )

    Event.sort(events, inplace=True, reverse=False)
    print(f"Returned {len(events)} event(s)")

    if not events:
        print("0 events found")
        return

    for evt in events:
        o_values = evt.get_tags_value("o")
        print(f"o values: {o_values}")
        print_event(evt, args.output)


if __name__ == "__main__":
    asyncio.run(do_query(get_args()))
