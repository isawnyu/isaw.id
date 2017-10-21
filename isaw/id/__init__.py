#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage unique ids for ISAW entities
"""

import better_exceptions
import logging
from datetime import datetime
from hashlib import blake2b

def make(content, namespace='', date_time=datetime.now(), id_length=3):

    stamp = bytes(date_time.isoformat(), encoding='ascii')
    if type(content) == str:
        data = content.encode('utf-8')
    else:
        data = bytes(content)
    data = stamp + data
    h = blake2b(data, digest_size=id_length)
    digest = h.hexdigest()
    if namespace != '':
        return '/{}/{}'.format(namespace, digest)
    else:
        return '/{}'.format(digest)
