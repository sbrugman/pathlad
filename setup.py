from setuptools import setup, find_packages

setup(
    name="pathlad",
    version="0.0.1",
    packages=find_packages("."),
    entry_points={
        "console_scripts": [
            "pathlad = pathlad.find_pattern:mainx"
        ]
    },
)
