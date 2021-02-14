from datetime import datetime
import json

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from solarapi.data import DeviceDoesNotExist, SolarDataBase
from solarapi.config import MYSQL

import logging

_LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()

data = SolarDataBase(*MYSQL)


@routes.get('/get/{device}/report/{year}/{month}/{day}')
async def get_device_report(req: Request):
    if 'device' in req.match_info and 'year' in req.match_info and 'month' in req.match_info and 'day' in req.match_info:
        device = req.match_info["device"]
        year = int(req.match_info["year"])
        month = int(req.match_info["month"])
        day = int(req.match_info["day"])

        try:
            report = await data.async_get_day_report(device, datetime(year, month, day))
        except DeviceDoesNotExist:
            return json_response({
                "error": "device does not exist"
            })

        return json_response({
            "report": report
        })

    return json_response({
        "error": "missing fields"
    })


@routes.get('/get/devices')
async def get_devices_list(req: Request):
    return json_response({
        "devices": await data.async_get_devices()
    })


async def add_routes_to(app):
    app.add_routes(routes)
