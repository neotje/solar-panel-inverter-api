from os import name
from setuptools import setup, find_packages

PROJECT_NAME = "SolarPaneInverterAPI"
PROJECT_PACKAGE_NAME = "solarapi"

PROJECT_GITHUB_USERNAME = "neotje"

PACKAGES = find_packages()

REQUIRED = [
    "aiohttp==3.7.3",
    "mysql-connector-python==8.0.23",
    "aiohttp_cors==0.7.0",
    "matplotlib==3.3.4"
]

setup(
    name=PROJECT_PACKAGE_NAME,
    packages=PACKAGES,
    install_requires=REQUIRED,
    entry_points={"console_scripts": [
        "solarapi = solarapi.__main__:main"
    ]}
)