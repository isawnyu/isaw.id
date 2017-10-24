#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test basic functionality of the isaw.id package
"""

from datetime import datetime
import glob
import isaw.id
from nose.tools import assert_equal, assert_raises
from os import remove
from os.path import dirname, join
import shutil


WHEN = datetime(2017, 10, 21, 6, 47, 18, 153304)

def test_make_defaults():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False)
    this = m.make(content='', date_time=WHEN)
    assert_equal(this, '/8c2dcb')

def test_make_content():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False)
    this = m.make(content='foo', date_time=WHEN)
    assert_equal(this, '/46ee55')

def test_make_namespace():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False)
    this = m.make(content='', namespace='foo', date_time=WHEN)
    assert_equal(this, '/foo/8c2dcb')

def test_make_namespace_default():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False,
        namespace='foo')
    this = m.make(content='', date_time=WHEN)
    assert_equal(this, '/foo/8c2dcb')

def test_make_namespace_content():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False)
    this = m.make(content='foo', namespace='bar', date_time=WHEN)
    assert_equal(this, '/bar/46ee55')

def test_make_namespace_default_content():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False,
        namespace='bar')
    this = m.make(content='foo', date_time=WHEN)
    assert_equal(this, '/bar/46ee55')

def test_make_length():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False)
    this = m.make(content='', date_time=WHEN, id_length=17)
    assert_equal(len(this), 17*2+1)
    assert_equal(this, '/c73b80d0146d6d03679c3077f9f05129db')

def test_make_length_default():
    global WHEN
    m = isaw.id.Maker(
        ensure_unique=False,
        id_length=17)
    this = m.make(content='', date_time=WHEN)
    assert_equal(len(this), 17*2+1)
    assert_equal(this, '/c73b80d0146d6d03679c3077f9f05129db')

def test_make_namespace_ensure():
    global WHEN
    path = join(dirname(__file__), 'data')
    src = join(path, 'nstest')
    dest = join(path, 'temptest')
    shutil.copy(src, dest)
    m = isaw.id.Maker(registry_path=path)
    this = m.make(content='foo', namespace='temptest', date_time=WHEN)
    # expect a collision, so algorithm adds a hex digit to the digest
    assert_equal(this, '/temptest/ee950528')
    del(m)
    remove(dest)
    for fn in glob.glob(join(path, '*.bak')):
        remove(fn)

def test_bad_register():
    global WHEN
    path = join(dirname(__file__), 'data')
    m = isaw.id.Maker(registry_path=path)
    assert_raises(IOError,
        m.make, content='foo', namespace='bogus', date_time=WHEN)

def test_saved():
    global WHEN
    path = join(dirname(__file__), 'data')
    src = join(path, 'nstest')
    dest = join(path, 'temptest')
    shutil.copy(src, dest)
    contents = 'The cat in the hat'.split()
    m = isaw.id.Maker(registry_path=path, namespace='temptest')
    for c in contents:
        m.make(content=c, date_time=WHEN)
    del(m)
    with open(dest, 'r') as f:
        results = f.read().splitlines()
    assert_equal(len(contents), len(results)-1)
    remove(dest)
    for fn in glob.glob(join(path, '*.bak')):
        remove(fn)
