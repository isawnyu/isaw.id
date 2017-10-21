#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test basic functionality of the isaw.id package
"""

import better_exceptions
from airtight.cli import configure_commandline
from airtight.logging import flog
import logging
from datetime import datetime
from nose.tools import assert_equal
import isaw.id

WHEN = datetime(2017, 10, 21, 6, 47, 18, 153304)

def test_make_defaults():
    global WHEN
    this = isaw.id.make(content='', date_time=WHEN)
    assert_equal(this, '/8c2dcb')

def test_make_content():
    global WHEN
    this = isaw.id.make(content='foo', date_time=WHEN)
    assert_equal(this, '/46ee55')

def test_make_namespace():
    global WHEN
    this = isaw.id.make(content='', namespace='foo', date_time=WHEN)
    assert_equal(this, '/foo/8c2dcb')