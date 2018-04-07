from string import Template
from twisted.internet.defer import inlineCallbacks
from twisted.enterprise import adbapi

ProgrammingError = Exception # FIXME

TOKEN_MAX = 65536

def connect(**kwargs):
    """ create new connection pool """
    dbpool = adbapi.ConnectionPool(
        "psycopg2",
        cp_min=3,
        cp_max=10,
        cp_noisy=True,
        cp_reconnect=True,
        user=kwargs['pg-username'],
        password=kwargs['pg-password'],
        host=kwargs['pg-host'],
        database=kwargs['pg-database']
    )

    return dbpool

def drop_schema(schema, **kwargs):
    "" ""
    if 'conn' in kwargs:
        conn = kwargs.pop('conn')
    else:
        conn = connect(**kwargs)

    sql = "DROP SCHEMA IF EXISTS %s CASCADE" % schema
    return conn.runOperation(sql)

@inlineCallbacks
def create_schema(machine, **kwargs):
    """ add a new schema to an existing db """
    if 'conn' in kwargs:
        conn = kwargs.pop('conn')
    else:
        conn = connect(**kwargs)

    schema = kwargs.get('schema_name', machine.name)

    yield conn.runOperation("CREATE schema %s" % schema)
    
    yield conn.runOperation("""
    CREATE DOMAIN %s.token as smallint CHECK(VALUE >= 0 and VALUE <= %i)
    """ % (schema, TOKEN_MAX))

    num_places = len(machine.machine['state'])
    columns = [''] * num_places
    vector = [''] * num_places
    delta = [''] * num_places

    for key, props  in  machine.net.places.items():
        i = props['offset']
        columns[i] = ' %s %s.token' % (key, schema)
        vector[i] = ' %s int4' % key
        delta[i] = " (state).%s + conn.%s" % (key, key)

    yield conn.runOperation("""
    CREATE TYPE %s.state as ( %s )
    """ % (schema, ','.join(columns)))

    yield conn.runOperation("""
    CREATE TYPE %s.vector as ( %s )
    """ % (schema, ','.join(vector)))

    yield conn.runOperation("""
    CREATE TYPE %s.event as (
      id varchar(32),
      oid varchar(255),
      rev int4
    )
    """ % (schema))

    yield conn.runOperation("""
    CREATE TYPE %s.event_payload as (
      id varchar(32),
      oid varchar(255),
      seq int4,
      action varchar(255),
      payload json,
      timestamp timestamp
    )
    """ % (schema))

    yield conn.runOperation("""
    CREATE TYPE %s.current_state as (
      id varchar(32),
      oid varchar(255),
      action varchar(255),
      rev int4,
      state %s.state,
      payload json,
      modified timestamp,
      created timestamp
    )
    """ % (schema, schema))

    initial_vector = machine.net.initial_vector()

    # KLUDGE: this seems to be a limitation of how default values are declared
    # this doesn't work when state vector has only one element
    # state %s.state DEFAULT (0), # FAILS
    # state %s.state DEFAULT (0,0), # WORKS
    if len(initial_vector) < 2:
        raise Exception('state vector must be an n-tuple where n >= 2')

    yield conn.runOperation("""
    CREATE TABLE %s.states (
      oid VARCHAR(256) PRIMARY KEY,
      rev int4 default 0,
      state %s.state DEFAULT %s::%s.state,
      created timestamp DEFAULT now(),
      modified timestamp DEFAULT now()
    );
    """ % (schema, schema, tuple(initial_vector), schema))

    yield conn.runOperation("""
    CREATE TABLE %s.transitions (
      action VARCHAR(255) PRIMARY KEY,
      vector %s.vector
    );
    """ % (schema, schema))

    for key, props  in  machine.net.transitions.items():
        yield conn.runOperation("""
        INSERT INTO %s.transitions values('%s', %s)
        """ % (schema, key, tuple(props['delta'])))

    yield conn.runOperation("""
    CREATE TABLE %s.events (
      oid VARCHAR(255) REFERENCES %s.states(oid) ON DELETE CASCADE ON UPDATE CASCADE,
      seq SERIAL,
      action VARCHAR(255) NOT NULL,
      payload jsonb DEFAULT '{}',
      hash VARCHAR(32) NOT NULL,
      timestamp timestamp DEFAULT NULL
    );
    """ % (schema, schema))

    yield conn.runOperation("""
    ALTER TABLE %s.events ADD CONSTRAINT %s_oid_seq_pkey PRIMARY KEY (oid, seq);
    """ % (schema, schema))

    yield conn.runOperation("""
    CREATE INDEX %s_hash_idx on %s.events (hash);
    """ % (schema, schema))


    function_template = Template("""
    CREATE OR REPLACE FUNCTION ${name}.vclock() RETURNS TRIGGER
    AS $MARKER
        DECLARE
            conn ${name}.vector;
            revision int4;
        BEGIN
            SELECT
                (vector).* INTO STRICT conn
            FROM
                ${name}.transitions
            WHERE
                action = NEW.action;

            UPDATE
              ${name}.states set 
                state = ( ${delta} ),
                rev = rev + 1,
                modified = now()
            WHERE
              oid = NEW.oid
            RETURNING
              rev into STRICT revision;

            NEW.seq = revision;
            NEW.hash = md5(row_to_json(NEW)::TEXT);
            NEW.timestamp = now();

            RETURN NEW;
        END
    $MARKER LANGUAGE plpgsql""")
    
    fn_sql = function_template.substitute(
        MARKER='$$',
        name=schema,
        var1='$1',
        var2='$2',
        var3='$3',
        delta=','.join(delta)
    )

    yield conn.runOperation(fn_sql)

    function_template = Template("""
    CREATE TRIGGER ${name}_dispatch
    BEFORE INSERT on ${name}.events
      FOR EACH ROW EXECUTE PROCEDURE ${name}.vclock();
    """)

    trigger_sql = function_template.substitute(name=schema)
    yield conn.runOperation(trigger_sql)

