from setuptools import setup, find_packages

setup(
    name="bitwrap-io",
    version="0.2.0",
    author="Matthew York",
    author_email="myork@stackdump.com",
    description="A blockchain-style python eventstore w/ LMDB or postgresql backend",
    license='MIT',
    keywords='PNML petri-net eventstore state-machine',
    packages=find_packages() + ['twisted.plugins'],
    include_package_data=True,
    install_requires=['cyclone==1.1', 'service-identity==16.0.0', 'pg8000==1.10.6'],
    long_description="""
# Bitwrap-io

A blockchain-style eventstore

### Reference

Read Martin Fowler's description of [Event Sourcing](http://martinfowler.com/eaaDev/EventSourcing.html).

Watch an event sourcing video from [Greg Young](https://www.youtube.com/watch?v=8JKjvY4etTY).

Learn more about our deterministic approach to Blockchains at our blog [blahchain.com](http://www.blahchain.com).

""",
    url="http://getbitwrap.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License"
    ],
)
