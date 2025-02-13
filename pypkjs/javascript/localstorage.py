from __future__ import absolute_import
__author__ = 'katharine'

import STPyV8 as v8
import errno
import logging
import os
import os.path
import sqlite3
logger = logging.getLogger("pypkjs.javascript.localstorage")

_storage_cache = {}  # This is used when filesystem-based storage is unavailable.

class SQliteDict:
    def __init__(self, connection, table):
        self.connection = connection
        self.table = table
        self.connection.execute("CREATE TABLE IF NOT EXISTS %s (key TEXT PRIMARY KEY, value TEXT)" % table)

    def __getitem__(self, key):
        cursor = self.connection.execute("SELECT value FROM %s WHERE key = ?" % self.table, (key,))
        row = cursor.fetchone()
        if row is None:
            raise KeyError(key)
        return row[0]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self.connection.execute("REPLACE INTO %s (key, value) VALUES (?, ?)" % self.table, (key, value))
        self.connection.commit()

    def __delitem__(self, key):
        self.connection.execute("DELETE FROM %s WHERE key = ?" % self.table, (key,))
        self.connection.commit()

    def __contains__(self, key):
        cursor = self.connection.execute("SELECT value FROM %s WHERE key = ?" % self.table, (key,))
        return cursor.fetchone() is not None

    def keys(self):
        cursor = self.connection.execute("SELECT key FROM %s" % self.table)
        return [row[0] for row in cursor.fetchall()]

    def clear(self):
        self.connection.execute("DELETE FROM %s" % self.table)
        self.connection.commit()

    def close(self):
        self.connection.close()

    def __iter__(self):
        cursor = self.connection.execute("SELECT key FROM %s" % self.table)
        for row in cursor:
            yield row[0]

    def __len__(self):
        cursor = self.connection.execute("SELECT COUNT(*) FROM %s" % self.table)
        return cursor.fetchone()[0]

class LocalStorage(object):
    def __init__(self, runtime, persist_dir=None):
        self.storage = None
        if persist_dir is not None:
            try:
                try:
                    os.makedirs(os.path.join(persist_dir, 'localstorage'))
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

                # sqlite connection
                self.sqlite_conn = sqlite3.connect(os.path.join(persist_dir, 'localstorage', str(runtime.pbw.uuid) + '.sqlite'))
                self.sqlite_conn.autocommit = True

                # storage is a mapping of localstorage table where there's two columns,
                # key and value
                self.storage = SQliteDict(self.sqlite_conn, 'localstorage')
            except IOError:
                pass
        if self.storage is None:
            logger.warning("Using transient store.")
            self.storage = _storage_cache.setdefault(str(runtime.pbw.uuid), {})

        runtime.register_syscall("localStorage.set", self.set)
        runtime.register_syscall("localStorage.get", self.get)
        runtime.register_syscall("localStorage.has", self.has)
        runtime.register_syscall("localStorage.delete", self.delete_)
        runtime.register_syscall("localStorage.keys", self.keys)
        runtime.register_syscall("localStorage.enumerate", self.enumerate)
        runtime.register_syscall("localStorage.clear", self.clear)
        runtime.register_syscall("localStorage.getItem", self.getItem)
        runtime.register_syscall("localStorage.setItem", self.setItem)
        runtime.register_syscall("localStorage.removeItem", self.removeItem)
        runtime.register_syscall("localStorage.key", self.key)

        runtime.run_js("""
        localStorage = new (function() {
            this.set = get_syscall_func('localStorage.set');
            this.get = get_syscall_func('localStorage.get');
            this.has = get_syscall_func('localStorage.has');
            this.delete = get_syscall_func('localStorage.delete');
            this.delete_ = get_syscall_func('localStorage.delete_');
            this.keys = get_syscall_func('localStorage.keys');
            this.enumerate = get_syscall_func('localStorage.enumerate');
            this.clear = get_syscall_func('localStorage.clear');
            this.getItem = get_syscall_func('localStorage.getItem'); 
            this.setItem = get_syscall_func('localStorage.setItem');
            this.removeItem = get_syscall_func('localStorage.removeItem');
        })();
        """)

    def get(self, p, name):
        return self.storage.get(str(name), v8.JSNull())

    def set(self, p, name, value):
        self.storage[str(name)] = str(value)
        return True

    def has(self, p, name):
        return name in self.storage

    def delete_(self, p, name):
        if name in self.storage:
            del self.storage[name]
            return True
        else:
            return False

    def keys(self, *p):
        return v8.JSArray(self.storage.keys())

    def enumerate(self):
        return v8.JSArray(self.storage.keys())

    def clear(self, *args):
        self.storage.clear()

    def getItem(self, name, *args):
        return self.get(None, name)

    def setItem(self, name, value, *args):
        self.set(None, name, value)

    def removeItem(self, name, *args):
        return self.delete_(None, name)

    def key(self, index, *args):
        if len(self.storage) > index:
            return self.storage.keys()[index]
        else:
            return v8.JSNull()

    def _shutdown(self):
        if hasattr(self.storage, 'close'):
            self.storage.close()
