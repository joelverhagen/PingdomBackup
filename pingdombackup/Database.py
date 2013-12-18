import sqlite3
from contextlib import closing

from .log import log

class Database:
    SCHEMA = (
        ('probes', (
            ('id', 'INTEGER PRIMARY KEY'),
            ('country', 'TEXT'),
            ('city', 'TEXT'),
            ('name', 'TEXT'),
            ('active', 'BOOLEAN'),
            ('hostname', 'TEXT'),
            ('ip', 'TEXT'),
            ('countryiso', 'TEXT')
        )),
        ('checks', (
            ('id', 'INTEGER PRIMARY KEY'),
            ('name', 'TEXT'),
            ('type', 'TEXT'),
            ('lasterrortime', 'INTEGER'),
            ('lasttesttime', 'INTEGER'),
            ('lastresponsetime', 'INTEGER'),
            ('status', 'TEXT'),
            ('resolution', 'INTEGER'),
            ('hostname', 'TEXT'),
            ('created', 'INTEGER')
        )),
        ('results', (
            ('id', 'INTEGER PRIMARY KEY'),
            ('checkid', 'INTEGER'),
            ('probeid', 'INTEGER'),
            ('time', 'INTEGER'),
            ('status', 'TEXT'),
            ('responsetime', 'INTEGER'),
            ('statusdesc', 'TEXT'),
            ('statusdesclong', 'TEXT')
        ))
    )

    def __init__(self, database):
        self.database = database
        self.conn = None
        self._initialize()

        # create a set for each table's columns
        self.table_columns = {}
        for table, columns in self.SCHEMA:
            self.table_columns[table] = set(map(lambda c: c[0], columns))

    def get_record_by_id(self, table, record_id):
        return self.get_record(table, where='id = ?', parameters=(record_id, ))

    def get_record(self, *args, **kwargs):
        kwargs['limit'] = 1
        records = self.get_records(*args, **kwargs)
        if len(records) == 0:
            return None
        return records[0]

    def get_records(self, table, where=None, order_by=None, limit=None, offset=None, parameters=tuple()):
        # construct the WHERE
        if where is None:
            where = ''
        else:
            where = ' WHERE {0}'.format(where)

        # construct the ORDER BY
        if order_by is None:
            order_by = ''
        else:
            order_by = ' ORDER BY {0}'.format(order_by)

        # construct the LIMIT
        if limit is None:
            limit = ''
        else:
            limit = ' LIMIT {0}'.format(limit)
        if limit != '' and offset is not None:
            limit = '{0} OFFSET {1}'.format(limit, offset)

        # construct the whole query
        query = 'SELECT * FROM {0}{1}{2}{3}'.format(table, where, order_by, limit)
        log.debug('SQLite: {0}'.format(query))

        with closing(self.conn.cursor()) as c:
            c.execute(query, parameters)
            return c.fetchall()

    def upsert_record(self, table, new_record):
        old_exists = self.record_exists(table, new_record['id'])
        if old_exists:
            self.update_record(table, new_record)
        else:
            self.insert_record(table, new_record)

    def record_exists(self, table, record_id):
        with closing(self.conn.cursor()) as c:
            c.execute('SELECT COUNT(*) FROM {0} WHERE id = ?'.format(table), (record_id, ))
            return c.fetchone()[0] > 0

    def insert_record(self, table, new_record):
        self.insert_records(table, [new_record])

    def insert_records(self, table, new_records):
        log.debug('SQLite: inserting {0} record(s) into table "{1}"'.format(len(new_records), table))
        if len(new_records) == 0:
            return

        # fill column values
        for record in new_records:
            self._fill_columns(table, record)

        keys = new_records[0].keys()

        # the column part of the INSERT query
        columns = ', '.join(keys)

        # the value part of the INSERT query
        placeholders = ', '.join(map(lambda k: ':{0}'.format(k), keys))

        # generate the full UPDATE query
        query = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table, columns, placeholders)

        # execute the query
        with closing(self.conn.cursor()) as c:
            c.executemany(query, new_records)
            self.conn.commit()

    def update_record(self, table, new_record):
        self.update_records(table, [new_record])

    def update_records(self, table, new_records):
        log.debug('SQLite: updating {0} record(s) in table "{1}"'.format(len(new_records), table))
        if len(new_records) == 0:
            return

        # fill column values
        for record in new_records:
            self._fill_columns(table, record)
        
        # value columns are all columns besides 'id'
        value_columns = list(new_records[0].keys())
        value_columns.remove('id')

        # the value part of the UPDATE query
        placeholders = ', '.join(map(lambda k: '{0} = :{0}'.format(k), value_columns))

        # generate the full UPDATE query
        query = 'UPDATE {0} SET {1} WHERE id = :id'.format(table, placeholders)

        # execute the query
        with closing(self.conn.cursor()) as c:
            c.executemany(query, new_records)
            self.conn.commit()

    def _fill_columns(self, table, record):
        record_keys = set(record.keys())
        table_keys = self.table_columns[table]
        if len(record_keys) == len(table_keys):
            return

        # determine which keys are missing
        missing_keys =  table_keys - record_keys

        # fill with null values
        for key in missing_keys:
            record[key] = None

    def _initialize(self):
        if self.conn is not None:
            return

        # connect
        self.conn = sqlite3.connect(self.database)
        self.conn.row_factory = sqlite3.Row

        # make sure the tables exist
        with closing(self.conn.cursor()) as c:
            for table, columns in self.SCHEMA:
                # generate the column declarations
                columns = ', '.join(map(lambda c: '{0} {1}'.format(*c), columns))

                # generate query
                query = 'CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, columns)

                c.execute(query)

            self.conn.commit()
