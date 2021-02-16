"""api routes
"""
from datetime import datetime
import json
import pathlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from aiohttp import hdrs, web
from aiohttp.web_request import Request
from aiohttp.web_response import StreamResponse, json_response
from aiohttp_cors.cors_config import CorsConfig

from solarapi.data import DeviceDoesNotExist, SolarDataBase
from solarapi.config import MYSQL
from solarapi import cache

import logging

_LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()

data = SolarDataBase(*MYSQL)


@routes.get('/get/{device}/graph_img/{year}/{month}/{day}')
async def get_device_report(req: Request):
    # check if request has all the info needed.
    if 'device' in req.match_info and 'year' in req.match_info and 'month' in req.match_info and 'day' in req.match_info:
        device = req.match_info["device"]
        year = int(req.match_info["year"])
        month = int(req.match_info["month"])
        day = int(req.match_info["day"])

        try:
            # path to image
            img = pathlib.Path(
                cache.__path__[0]) / f"{device}-{year}-{month}-{day}.png"

            # check if requested image is today or img does not exist.
            # if requested date is today or img does not exist generate a new image.
            t = datetime.today()
            if (t.year == year and t.month == month and t.day == day) or not img.is_file(): # only interested in date not time.
                _LOGGER.info("creating new image...")

                # get day report
                report = await data.async_get_day_report(device, datetime(year, month, day))

                time_fmt = mdates.DateFormatter('%H-%M') # time formatter for time axis.
                fig, ax = plt.subplots() # matplotlib fig and axis

                # convert day report to plot data.
                x = []
                y = []
                for row in report:
                    x.append(datetime.fromtimestamp(row['time'] / 1000.0))
                    y.append(row['PAC'])

                # plot data
                ax.plot(x, y, label="pac")

                # add labels, title and grid to fig.
                ax.xaxis.set_major_formatter(time_fmt)
                ax.set_ylabel("Ouput in Watt")
                ax.set_xlabel("Time")
                plt.xticks(rotation=45)
                plt.title(f"{device} {year}-{month}-{day}", loc='left')
                ax.grid()

                # save figure.
                fig.tight_layout()
                fig.savefig(img, dpi=300)

            # create stream response to write image to.
            resp = StreamResponse(headers={'Content-Type': 'image/png'})

            # add cors headers
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "*"
            resp.headers[hdrs.ACCESS_CONTROL_EXPOSE_HEADERS] = "*"
            if req.headers.get(hdrs.ORIGIN) is not None:
                resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = req.headers.get(
                    hdrs.ORIGIN)
            else:
                resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
            
            await resp.prepare(req)

            # open image as binary and write lines to the stream response
            file = img.open('rb')
            for line in file.readlines():
                await resp.write(line)

            await resp.write_eof()
            file.close()

        except DeviceDoesNotExist:
            resp = json_response({
                "error": "device does not exist"
            })

        return resp

    return json_response({
        "error": "missing fields"
    })


@routes.get('/get/{device}/report/{year}/{month}/{day}')
async def get_device_report(req: Request):
    if 'device' in req.match_info and 'year' in req.match_info and 'month' in req.match_info and 'day' in req.match_info:
        device = req.match_info["device"]
        year = int(req.match_info["year"])
        month = int(req.match_info["month"])
        day = int(req.match_info["day"])

        try:
            report = await data.async_get_day_report(device, datetime(year, month, day))
            
            resp = json_response({
                "report": report,
            })
        except DeviceDoesNotExist:
            resp = json_response({
                "error": "device does not exist"
            })

        if req.headers.get(hdrs.ORIGIN) is not None:
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = req.headers.get(
                hdrs.ORIGIN)
        else:
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"

        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "*"

        return resp

    return json_response({
        "error": "missing fields"
    })


# @routes.get('/get/devices')
async def get_devices_list(req: Request):
    return json_response({
        "devices": await data.async_get_devices()
    })


async def add_routes_to(app: web.Application, cors: CorsConfig):
    res = cors.add(app.router.add_resource("/get/devices"))
    cors.add(res.add_route("GET", get_devices_list))

    #res2 = cors.add(app.router.add_resource("/get/{device}/report/{year}/{month}/{day}"))
    #cors.add(res2.add_route("GET", get_device_report))

    app.add_routes(routes)
