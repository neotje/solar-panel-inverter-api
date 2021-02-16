import asyncio
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from solarapi.data import SolarDataBase
from solarapi.config import MYSQL

data = SolarDataBase(*MYSQL)

async def main():
    devices = await data.async_get_devices()
    report = await data.async_get_day_report(devices[0], datetime(2021, 2, 14))

    fig, ax = plt.subplots()

    x = []
    y = []

    for row in report:
        x.append(datetime.fromtimestamp(row['time'] / 1000.0))
        y.append(row['PAC'])

    pac_line = ax.plot(x, y, label="pac")
    ax.set_ylabel("Ouput in Watt")
    ax.set_xlabel("Time")

    plt.xticks(rotation=45)

    ax.grid()

    fig.tight_layout()
    fig.savefig("test.png")




asyncio.run(main())