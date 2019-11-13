"""
See https://matrix.org/docs/guides/usage-of-matrix-nio
and https://github.com/poljar/matrix-nio
"""

from importlib import util
import asyncio
from nio import AsyncClient, LoginResponse, SyncResponse, RoomMessageText

import argparse
import configparser
import logging
import sys

import tztipbot

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    config = configparser.ConfigParser()
    with open("config") as config_file:
        config.read_file(config_file)
    logger.debug(f"{config['client']['homeserver'], config['client']['username']}")

    async_client = AsyncClient(
        config["client"]["homeserver"], config["client"]["username"]
    )
    try:
        asyncio.run(amain(async_client, config))
    except KeyboardInterrupt:
        logger.info("keyboard interrupt")
    except:
        logger.exception("async.run failed")


async def amain(client, config):
    try:
        response = await client.login(config["client"]["password"])
        if isinstance(response, LoginResponse):
            handle_login_response(client, response)
        else:
            logger.error(f"unexpected login response: {type(response)}: {response}")
            return

        try:
            with open("next_batch", "r") as next_batch_token:
                client.next_batch = next_batch_token.read()
        except FileNotFoundError:
            pass

        tzbot = tztipbot.TzTipBot(config["node"]["uri"])

        get_full_state = True  # request full state on first sync only
        while True:
            response = await client.sync(30000, full_state=get_full_state)
            if isinstance(response, SyncResponse):
                await handle_sync_response(client, response, tzbot)
                get_full_state = False
            else:
                logger.error(f"unexpected response type: {type(response)}: {response}")

    except asyncio.CancelledError:
        logger.info(f"asyncio cancellederror")

    finally:
        # It seems that we can only close our async client from within this
        # async function, which is why we catch exceptions here.
        await client.close()


def handle_login_response(client, response):
    logger.info(f"login response: {response}")


async def handle_sync_response(client, response, tzbot):
    logger.debug(f"sync response: {response}")

    with open("next_batch", "w") as next_batch_token:
        next_batch_token.write(response.next_batch)

    for room_id, room in response.rooms.join.items():
        display_name = client.rooms[room_id].display_name

        if len(room.timeline.events) > 0:
            for event in room.timeline.events:
                if isinstance(event, RoomMessageText):
                    logger.info(
                        f'message in "{display_name}" from {event.sender}: {event.body}'
                    )

                    outputs = tzbot.received_message(
                        {"room": room_id, "sender": event.sender, "body": event.body}
                    )

                    for output in outputs:
                        await client.room_send(room_id, "m.room.message", output)

                else:
                    logger.info(f"event: {type(event)}: {event}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="bot based on matrix-nio")
    parser.add_argument("--debug", "-d", action="store_true")
    args = parser.parse_args()
    logger.debug(f"args = {args}")
    if args.debug:
        logger.setLevel(logging.DEBUG)

    main()
