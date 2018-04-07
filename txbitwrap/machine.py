""" load xml definitions as a bitwrap state machine """

import os
from glob import glob
import xml.etree.ElementTree as ET # XML parser
import time # timestamp for id generation
from random import randint # random number for id generation

PNML_PATH = os.environ.get('PNML_PATH', os.path.abspath(__file__ + '/../examples'))

def set_pnml_path(pnml_dir):
    """ set path to pnml files """
    global PNML_PATH
    PNML_PATH = pnml_dir

def schema_to_file(name):
    """ build schema filename from name """
    return os.path.join(PNML_PATH, '%s.xml' % name)

def schema_files():
    """ list schema files """
    return glob(PNML_PATH + '/*.xml')

def schema_list():
    """ list schema files """
    return [os.path.basename(xml)[:-4] for xml in schema_files()]

def parse_pnml_file(filename):
    """ This method parse all Petri nets of the given file.  """
    tree = ET.parse(filename) # parse XML with ElementTree
    root = tree.getroot()

    nets = [] # list for parsed PetriNet objects

    for net_node in root.iter('net'):
        # create PetriNet object
        net = PetriNet()
        nets.append(net)
        net.name = net_node.get('id')

        # and parse transitions
        for transition_node in net_node.iter('transition'):
            transition = Transition()
            transition.id = transition_node.get('id')
            transition.label = transition.id
            off_node = transition_node.find('./name/graphics/offset')
            transition.offset = [float(off_node.get('x')), float(off_node.get('y'))]
            position_node = transition_node.find('./graphics/position')
            transition.position = [float(position_node.get('x')), float(position_node.get('y'))]

            net.transitions[transition.id] = transition
            transition.net = net

        # and parse places
        for place_node in net_node.iter('place'):
            place = Place()
            place.id = place_node.get('id')
            place.label = place.id
            off_node = place_node.find('./name/graphics/offset')
            place.offset = [float(off_node.get('x')), float(off_node.get('y'))]
            position_node = place_node.find('./graphics/position')
            place.position = [float(position_node.get('x')), float(position_node.get('y'))]

            marking_str = place_node.find('./initialMarking/value')

            if marking_str.text:
                place.marking = int(marking_str.text.split(',')[1])
            else:
                place.marking = 0

            net.places[place.id] = place

        # and arcs
        for arc_node in net_node.iter('arc'):
            edge = Edge()
            net.edges.append(edge)

            edge.id = arc_node.get('id')
            edge.source = arc_node.get('source')
            edge.target = arc_node.get('target')
            #edge.inscription = float(arc_node.find('./inscription/text').text)
            arc_type = arc_node.find('type').get('value')

            if arc_type == 'inhibitor':
                # TODO use edge.source to determine if this arc expresses a role or
                # if the source yields a token
                # record 'roles' accordingly
                edge.inhibitor = True

            edge.net = net

    return nets

class PetriNet(object):
    """ This class represents a Petri net.
    Original author: Copyright (c) 2015 Thomas Irgang
    see MIT license: https://github.com/irgangla/pntools/blob/master/LICENSE

    This class represents a Petri net. A Petri net consists of
    a set of labelled labelled transitions, labelled places and
    arcs from places to transitions or transitions to places.

    net.edges: List of all edges of this Petri net
    net.transitions: Map of (id, transition) of all transisions of this Petri net
    net.places: Map of (id, place) of all places of this Petri net
    """

    def __init__(self):
        self.edges = [] # List or arcs
        self.transitions = {} # Map of transitions. Key: transition id, Value: event
        self.places = {} # Map of places. Key: place id, Value: place
        self.roles = [] # use roles to model inhibitor arc actors
        self.name = None

    def __str__(self):
        text = '--- Net: ' + self.name + '\nTransitions: '
        for transition in self.transitions.values():
            text += str(transition) + ' '
        text += '\nPlaces: '
        for place in self.places.values():
            text += str(place) + ' '
        text += '\n'
        for edge in self.edges:
            text += str(edge) + '\n'
        text += '---'

        return text

class Transition(object):
    """
    This class represents a labelled transition of a Petri net.
    A transition represents an activity.
    """

    def __init__(self):
        self.label = "Transition" # default label of event
        #generate a unique id
        self.id = ("Transition" + str(time.time())) + str(randint(0, 1000))
        self.offset = [0, 0]
        self.position = [0, 0]
        self.net = None

    def __str__(self):
        return self.label


class Place(object):
    """ This class represents a labelled Place of a Petri net.  """

    def __init__(self):
        self.label = "Place" # default label of event
        #generate a unique id
        self.id = ("Place" + str(time.time())) + str(randint(0, 1000))
        self.offset = [0, 0]
        self.position = [0, 0]
        self.marking = 0

    def __str__(self):
        return self.label


class Edge(object):
    """ This class represents an arc of a Petri net.  """

    def __init__(self):
        #generate a unique id
        self.id = ("Arc" + str(time.time())) + str(randint(0, 1000))
        self.source = None # id of the source event of this arc
        self.target = None # id of the target event of this arc
        self.inscription = "1" # inscription of this arc
        self.net = None # Reference to net object for label resolution of source an target

        self.inhibitor = False
        self.role = None

    def find_source(self):
        """ find source of txn """
        if self.source in self.net.transitions:
            return self.net.transitions[self.source]

        return self.net.places[self.source]

    def find_target(self):
        """ find txn target """
        if self.target in self.net.transitions:
            return self.net.transitions[self.target]

        return self.net.places[self.target]

    def __str__(self):
        return str(self.find_source()) + "-->" + str(self.find_target())


class Machine(object):
    """ Use a petri-net as a state machine """

    def __init__(self, name):
        self.name = name
        self.net = PTNet(name)
        self.machine = self.net.to_machine()

class PTNet(object):
    """ wrapper to convert PetriNet into a P/T state machine """

    def __init__(self, name):
        self.name = name
        self.places = None
        self.transitions = None
        self.filename = schema_to_file(name)
        self.net = parse_pnml_file(self.filename)[0]

        # reindex
        Convert.append_roles(self.net)
        self.places = Convert.places(self.net)
        self.transitions = Convert.transitions(self.net, self.places)
        Convert.apply_edges(self.net, self.places, self.transitions)

    def empty_vector(self):
        """ return an empty state-vector """
        return [0] * len(self.places)

    def initial_vector(self):
        """ return initial state-vector """
        vector = self.empty_vector()

        for _, place in self.places.items():
            vector[place['offset']] = place['initial']

        return vector

    def to_machine(self):
        """ open p/t-net """

        return {
            'state': self.initial_vector(),
            'transitions': self.transitions
        }

class Convert(object):
    """ helpers to create a bitwrap machine from a petri-net """

    @staticmethod
    def append_roles(net):
        """ build roles from edge list """

        for edge in net.edges:
            if edge.inhibitor and ('_role' in edge.source):
                role_name = edge.source.replace('_role', '')

                if role_name not in net.roles:
                    net.roles.append(role_name)

                edge.role = role_name # set required role

    @staticmethod
    def places(net):
        """ build place vector definition """

        _places = {}
        offset = 0

        for place in net.places:

            # KLUDGE: refactor 'role' conventions to be more explicit
            if not '_role' in place:
                _places[place] = {
                    'offset': offset,
                    'position': net.places[place].position,
                    'initial': net.places[place].marking
                }

                offset += 1

        return _places

    @staticmethod
    def empty_vector(size):
        """ return an empty vector of given size """
        return [0] * size

    @staticmethod
    def transitions(net, net_places):
        """ build set of transitions from network """

        _transitions = {}

        for action in net.transitions:
            _transitions[action] = {
                'delta': Convert.empty_vector(len(net_places)),
                'position': net.transitions[action].position,
                'role': 'default'
            }

        return _transitions

    @staticmethod
    def apply_edges(net, net_places, net_transitions):
        """ re-index edges and places """

        for edge in net.edges:
            source = edge.find_source()
            target = edge.find_target()

            if isinstance(source, Transition):
                if edge.inhibitor is True:
                    raise Exception('Roles cannot be targets')
                else:
                    offset = net_places[target.id]['offset']
                    net_transitions[source.id]['delta'][offset] = 1

            elif isinstance(source, Place):
                if edge.inhibitor is True:
                    net_transitions[target.id]['role'] = edge.role
                else:
                    offset = net_places[source.id]['offset']
                    net_transitions[target.id]['delta'][offset] = -1
            else:
                raise Exception('invalid edge %s' % edge.id)
