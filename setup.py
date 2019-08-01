from setuptools import setup, find_packages

setup(
    name="jco",
    version="0.1.0",
    description="Jonathan's Converter, for working with hex and binary numbers",
    packages=find_packages(),
    entry_points={"console_scripts": ["jco=jco.script:entry"]},
)
