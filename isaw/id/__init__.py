#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage unique ids for ISAW entities
"""

import logging
from datetime import datetime
from hashlib import blake2b
from os.path import abspath, isdir, join, realpath
import sys
import shutil


DEFAULT_ID_LENGTH = 3
DEFAULT_NAMESPACE = ''
MAX_TRIES = 10

class Maker:

    def __init__(
        self,
        ensure_unique=True,
        registry_path=None,
        namespace=DEFAULT_NAMESPACE,
        id_length=DEFAULT_ID_LENGTH):

        self.ensure = ensure_unique
        if self.ensure:
            if not registry_path:
                raise ValueError(
                    'Maker initialized with ensure_unique=True but no '
                    'registry_path was provided.')
            else:
                path = abspath(realpath(registry_path))
                if isdir(path):
                    self.registry_path=registry_path
                    self.registry = {}
                else:
                    raise IOError(
                        'Make initialized with registry_path="{}", but it is '
                        'not a directory.')
        self.namespace = namespace
        self.id_length = id_length


    def __del__(self):
        if self.ensure:
            for k, v in self.registry.items():
                path = join(self.registry_path, k)
                stamp = datetime.now().isoformat()
                shutil.copy2(path, '{}.{}.bak'.format(path, stamp))
                with open(path, 'w') as f:
                    f.write('\n'.join(list(v)))

    def make(
        self,
        content,
        namespace=None,
        date_time=datetime.now(),
        id_length=None):

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
            while not self._ok(ns, digest):
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


    def _ok(self, ns, digest):
        r = self._load_register(ns)
        return not(digest in r)


    def _register(self, ns, digest):
        self.registry[ns].add(digest)


    def _load_register(self, ns):
        try:
            r = self.registry[ns]
        except KeyError:
            logger = logging.getLogger(sys._getframe().f_code.co_name)
            path = join(self.registry_path, ns)
            try:
                f = open(path, 'r')
            except IOError as e:
                raise IOError(
                    'Failed to open register {} from file "{}"'
                    ''.format(ns, path)
                    ).with_traceback(e.__traceback__)
            else:
                r = set(f.read().splitlines())
                logger.info(
                    'Read {} ids from register file "{}"'
                    ''.format(len(r), path))
                self.registry[ns] = r
        return r



