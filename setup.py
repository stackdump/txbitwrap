from setuptools import setup, find_packages

setup(
    name="txbitwrap",
    version="0.2.0",
    author="Matthew York",
    author_email="myork@stackdump.com",
    description="bitwrap eventstore deployed as a Twisted plugin",

    license='MIT',
    keywords='PNML petri-net eventstore state-machine',
    packages=find_packages() + ['twisted.plugins'],
    include_package_data=True,
    install_requires=[
        'cyclone==1.1',
        'service-identity==16.0.0',
        'txRDQ==0.2.14',
        'txAMQP==0.7.0',
        'bitwrap-machine',
        'bitwrap-psql'],

    long_description="""
txbitwrap

Deploy and manage bitwrap eventstore as a twistd service.
https://twistedmatrix.com

""",
    url="http://getbitwrap.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License"
    ],
)
