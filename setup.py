from setuptools import setup

setup(
    name="djsonld",
    description="A django tools for using JSON-LD in a template",
    packages=[
        "djsonld",
    ],
    install_requires=[
        "PyLD",
    ],
)
