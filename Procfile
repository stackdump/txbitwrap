api: PNML_PATH=./schemata PYTHONPATH=./ twistd -n bitwrap --listen-ip=0.0.0.0 --listen-port=8080 --queue=bitwrap --exchange=bitwrap --routing-key='*'
X: PYTHONPATH=./ twistd -ny apps/player-X.tac --pidfile player-x.pid -l -
O: PYTHONPATH=./ twistd -ny apps/player-O.tac --pidfile player-o.pid -l -
