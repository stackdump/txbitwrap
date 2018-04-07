class Simulation(object):
    """ use pnet to run a simulation """

    def __init__(self, oid, net, control):
        self.pnet = net
        self.ctl = control
        self.history = []
        self.hilight_live_transitions()
        self.oid = oid

    def state_vector(self):
        """ return current state vector from token_ledger """
        vector = [0] * self.pnet.vector_size

        for name, attr  in self.pnet.place_defs.items():
            vector[attr['offset']] = self.pnet.token_ledger[name]

        return vector

    def commit(self, action, input_state=None, dry_run=False):
        """ transform state_vector """
        out = [0] * self.pnet.vector_size

        if not input_state:
            state = self.state_vector()
        else:
            state = input_state

        txn = self.pnet.transition_defs[action]['delta']

        for i in range(0, self.pnet.vector_size):
            out[i] = state[i] + txn[i]
            if out[i] < 0:
                return False

        if not dry_run:
            self.pnet.update(out)

        return True

    def is_alive(self, action, from_state=None):
        """ test that input transition can fire """
        return  self.commit(action, input_state=from_state, dry_run=True)

    def trigger(self, event):
        """ callback to trigger live transition during simulation """
        target_id = str(event.target.id)

        if not self.ctl.is_selectable(target_id):
            return

        refid, symbol = target_id.split('-')

        if not self.pnet or not symbol == 'transition':
            return

        if self.commit(refid):
            self.history.append(refid)
            self.ctl.reset(callback=self.redraw)

        return refid

    def reset(self):
        """ render SVG and hilight live transitions """
        self.pnet.reset_tokens()
        self.ctl.reset(callback=self.ctl.render)

    def redraw(self):
        """ render SVG and hilight live transitions """
        self.ctl.render()
        self.hilight_live_transitions()

    def hilight_live_transitions(self):
        """ visually indiciate which transitions can fire """
        current_state = self.state_vector()

        for action in self.pnet.transitions.keys():
            if self.is_alive(action, from_state=current_state):
                self.pnet.handles[action].attr({ 'fill': 'red' })

