"""solarapi core

creates aiohttp app and adds routes from solarapi.api.

then start server.
"""
import asyncio
from solarapi.api import add_routes_to
from aiohttp import web
import aiohttp_cors
import sys

import logging

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(funcName)s:[%(lineno)d]   %(message)s'
)
_LOGGER = logging.getLogger(__name__)

def run():
    _LOGGER.info("Starting Solar Panel Inverter API...")

    try:
        asyncio.run(async_run())
    except KeyboardInterrupt:
        pass


async def async_run():
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_headers="*",
            expose_headers="*"
        )
    })

    await add_routes_to(app, cors)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "192.168.111.31", 9124)
    await site.start()

    _LOGGER.info(f"Solar API server started on: {site._host}:{site._port}")

    while True:
        await asyncio.sleep(3600)