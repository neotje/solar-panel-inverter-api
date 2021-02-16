"""solar-panel-inverter-logger database wrapper"""
import mysql.connector
import datetime

import logging

_LOGGER = logging.getLogger(__name__)


class SolarDataBase:
    def __init__(self, host: str, user: str, password: str, database: str):
        """SolarDataBase

        Args:
            host (str): mysql host
            user (str): mysql user
            password (str): mysql user password
            database (str): database name
        """
        self._db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    async def async_get_day_report(self, device: str, day: datetime.datetime):
        """Get day report from a device.

        Args:
            device (str): device name
            day (datetime.datetime): day start at 00:00

        Raises:
            DeviceDoesNotExist: device does not exist.

        Returns:
            list: array with database rows as dictonaries.
        """
        start = unix_time_millis(day)
        end = unix_time_millis(day + datetime.timedelta(days=1))

        cursor = self._db.cursor(dictionary=True)

        try:
            cursor.execute(
                f"SELECT * FROM {device} WHERE time BETWEEN {start} AND {end}")
        except mysql.connector.errors.ProgrammingError:
            raise DeviceDoesNotExist

        result = cursor.fetchall()

        return result

    async def async_get_devices(self):
        """Get list of devices.

        Returns:
            list: array of device names.
        """
        cursor = self._db.cursor()
        cursor.execute("show tables")

        result = cursor.fetchall()
        arr = []

        for x in result:
            arr.append(x[0])

        return arr


epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


class DeviceDoesNotExist(Exception):
    pass
