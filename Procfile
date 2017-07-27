api: twistd -n bitwrap --listen-ip=0.0.0.0 --listen-port=8080 --queue=bitwrap --exchange=bitwrap --routing-key='*'
keen: twistd -ny apps/keenio.tac --pidfile keen.pid -l -
X: twistd -ny apps/player-X.tac --pidfile player-x.pid -l -
O: twistd -ny apps/player-O.tac --pidfile player-o.pid -l -
meta: twistd -ny apps/meta.tac --pidfile meta.pid -l -
