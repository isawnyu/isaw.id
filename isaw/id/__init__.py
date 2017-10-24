#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage unique ids for ISAW entities

Defines the class Maker(), which provides all functionality of the package.
"""

import logging
from datetime import datetime
from hashlib import blake2b
from os import makedirs
from os.path import abspath, isdir, join, realpath
import sys
from shutil import copy2, rmtree


DEFAULT_ID_LENGTH = 3
DEFAULT_NAMESPACE = ''
MAX_TRIES = 10

class Maker:
    """Make unique IDs for ISAW entities, optionally within a namespace.

    Public methods:
    make() -- creates an ID based on content bytes and datetime stamp

    Default behavior is to create unique IDs using the BLAKE2 cryptographic
    hash functions, providing as input a series of content bytes and a
    datetime stamp in ISO format and checking the result for uniqueness within
    an arbitrary namespace as documented by a registry file. Registry file
    contents (text files with one hash hexdigest per line) are loaded on
    demand, but persist in memory until the maker instance that loaded them
    is destroyed. On destruction, the instance attempts to write back to file
    any ids added to loaded registries after create a .bak file of the prior
    version.
    """

    def __init__(
        self,
        ensure_unique=True,
        registry_path=None,
        namespace=DEFAULT_NAMESPACE,
        id_length=DEFAULT_ID_LENGTH):
        """Initialize the Maker() class.

        Keyword arguments:
        ensure_unique -- ensure ID uniqueness within a namespace by checking
                         a corresponding registry
        registry_path -- path to directory containing namespace registry files
        namespace -- string to use for default namespace in id generation
        id_length -- default number of hex digits to use in the id hash
        """

        self.ensure = ensure_unique
        if self.ensure:
            if not registry_path:
                raise ValueError(
                    'Maker initialized with ensure_unique=True but no '
                    'registry_path was provided.')
            path = abspath(realpath(registry_path))
            if isdir(path):
                self.registry_path=registry_path
                self.registry = {}
                self.dirty = {}
            else:
                raise IOError(
                    'Make initialized with registry_path="{}", but it is '
                    'not a directory.')
        self.namespace = namespace
        self.id_length = id_length


    def __del__(self):
        """Teardown a Maker instance.

        If the instance was instantiated with ensure_unique=True, attempt to
        write any new values to file.
        """

        if self.ensure:
            for k, v in self.registry.items():
                try:
                    dirty = self.dirty[k]
                except KeyError:
                    pass
                else:
                    if dirty:
                        path = join(self.registry_path, k)
                        stamp = datetime.now().isoformat()
                        copy2(path, '{}.{}.bak'.format(path, stamp))
                        with open(path, 'w') as f:
                            f.write('\n'.join(list(v)))
            if len(self.registry) > 0:
                rmtree(join(self.registry_path, 'tmp'))

    def make(
        self,
        content,
        namespace=None,
        date_time=datetime.now(),
        id_length=None):
        """Generate an id.

        Keyword arguments:
        content -- zero or more bytes of content to give to the hash function
        namespace -- optional string to use for namespace in ID generation
        date_time -- a datetime object that is converted to an isoformat stamp
                     and appended to the content before hash generation
        id_length -- optional number of hex values to use in the id

        This method creates ID strings like '/46ee55' when namespace == '' and
        '/foo/8c2dcb' when namespace == 'foo'.
        """

        stamp = bytes(date_time.isoformat(), encoding='ascii')
        if type(content) == str:
            data = content.encode('utf-8')
        else:
            data = bytes(content)
        data = stamp + data
        if id_length is not None:
            length = id_length
        else:
            length = self.id_length
        h = blake2b(data, digest_size=length)
        digest = h.hexdigest()
        if namespace is None:
            ns = self.namespace
        else:
            ns = namespace
        if self.ensure:
            tries = 0
            while not self._unique(ns, digest):
                if tries == 0:
                    logger = logging.getLogger(sys._getframe().f_code.co_name)
                logger.warning(
                    'hash collision with "{}"'.format(digest))
                if tries >= MAX_TRIES:
                    raise ValueError(
                        'Could not find unique hash after {} tries.'
                        ''.format(tries))
                length += 1
                h = blake2b(data, digest_size=length)
                digest = h.hexdigest()
                tries += 1
            self._register(ns, digest)
        if ns != '':
            return '/{}/{}'.format(ns, digest)
        else:
            return '/{}'.format(digest)


    def _unique(self, ns, digest):
        """Test if digest is in a namespace registry."""
        r = self._load_register(ns)
        return not(digest in r)


    def _register(self, ns, digest):
        """Add a new digest to a namespace registry."""
        self.registry[ns].add(digest)
        self.dirty[ns] = True


    def _load_register(self, ns):
        """Load a namespace registry file from storage to memory."""
        try:
            r = self.registry[ns]
        except KeyError:

            # stash an unaltered copy of the file in case something goes wrong
            path_tmp = join(self.registry_path, 'tmp')
            makedirs(path_tmp, exist_ok=True)
            path = join(self.registry_path, ns)
            copy2(path, join(path_tmp, ns))

            # read the file
            try:
                f = open(path, 'r')
            except IOError as e:
                raise IOError(
                    'Failed to open register {} from file "{}"'
                    ''.format(ns, path)
                    ).with_traceback(e.__traceback__)
            else:
                r = set(f.read().splitlines())
                logger = logging.getLogger(sys._getframe().f_code.co_name)
                logger.info(
                    'Read {} ids from register file "{}"'
                    ''.format(len(r), path))
                self.registry[ns] = r
        return r



