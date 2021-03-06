from setuptools import setup, find_packages

setup(
    name="txbitwrap",
    version="0.4.0",
    author="Matthew York",
    author_email="myork@stackdump.com",
    description="bitwrap eventstore deployed as a Twisted plugin",

    license='MIT',
    keywords='PNML petri-net eventstore state-machine',
    packages=find_packages() + ['twisted.plugins'],
    include_package_data=True,
    install_requires=[
        'ujson==1.35',
        'service-identity==16.0.0',
        'txRDQ==0.2.14',
        'psycopg2==2.7.4',
        'txAMQP==0.7.0'],

    long_description="""
txbitwrap

Deploy and manage bitwrap eventstore as a twistd service.
https://twistedmatrix.com

""",
    url="http://getbitwrap.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License"
    ],
)
