from setuptools import setup, find_packages

setup(
    name="pathlad",
    version="0.0.2",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pathlad = pathlad.find_pattern:main_pathlad"
        ]
    },
)
