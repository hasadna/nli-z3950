from setuptools import setup, find_packages
import os, time


if os.path.exists("VERSION.txt"):
    # this file can be written by CI tools (e.g. Travis)
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip().strip("v")
else:
    version = str(time.time())


setup(
    name="nli-z3950",
    version=version,
    packages=["nli_z3950"],
    url='https://github.com/hasadna/nli-z3950',
    license='MIT',
)
