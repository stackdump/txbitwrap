# txbitwrap

[![Build Status](https://travis-ci.org/stackdump/txbitwrap.svg?branch=master)](https://travis-ci.org/stackdump/txbitwrap)

An event-oriented service using a PostgreSQL database as an eventstore.
Fork of http://getbitwrap.com

This library is build to run atop an event-driven networking engine called: [Twisted](https://twistedmatrix.com/trac/)

### Status

Working to refine UI features written in [brython](https://www.brython.info/)

### Benchmark

Testing using [Apache bench](https://httpd.apache.org/docs/2.4/programs/ab.html)

**Setup**

Running Twisted w/ Python 2.7, Postgres 9.5, and RabbitMQ 3.5.7

All services stacked on a single Ubuntu cloud node:

`512 MB RAM, 1 vCPU, 20 GB SSD`

Hosting Cost:

`$5/mo`

```
URL='http://api.example.com:8080/dispatch/test/foo/INC_0'
ab -n 300 -c 300 -p post_data.txt ${URL}
```

**Result**

Able to sustain `300` concurrency with ~ `315 req/s`

```
Server Software:        txbitwrap/v0.4.0
Server Hostname:        api.example.com
Server Port:            8080

Document Path:          /dispatch/test/foo/INC_0
Document Length:        70 bytes

Concurrency Level:      300
Time taken for tests:   0.952 seconds
Complete requests:      300
Failed requests:        0
Total transferred:      106800 bytes
Total body sent:        53400
HTML transferred:       21000 bytes
Requests per second:    315.04 [#/sec] (mean)
Time per request:       952.250 [ms] (mean)
Time per request:       3.174 [ms] (mean, across all concurrent requests)
Transfer rate:          109.53 [Kbytes/sec] received
                        54.76 kb/s sent
                        164.29 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       65   97  18.2     93     136
Processing:    78  263 157.9    208     800
Waiting:       78  263 157.8    208     800
Total:        145  360 167.4    306     911
```

#### Demo - Tic-Tac-Toe

* Try sending game events yourself
  * using manual events trigger by clicking the board in-browser

```
./entry.sh api
```


OR 

* use the apps/player-X.tac apps/player-O.tac files
  * to simulate a game using random play event processors

```
./entry.sh api X O
```

Then 

* visit http://127.0.0.1:8080 to see the Petri-Net editor
* click 'Reset' to create a new game
  * if running X & O workers - you will see the game progress on its own
  * otherwise click on the Petri-Net to make moves manually


#### Docker

[![Docker](https://img.shields.io/docker/automated/stackdump/txbitwrap.svg)](https://hub.docker.com/r/stackdump/txbitwrap/~/dockerfile/)

You may use the included docker-compose.yaml to setup a development environment.

#### Testing

See tests under txbitwrap.tests -- `it is recommended to only run a single test at a time.`

Not all test code plays nice w/ the reactor,
if needed -- convert to warnings using the --unclean-warnings arg and don't fail the test.

```
trial --unclean-warnings
```

