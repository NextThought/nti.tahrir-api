#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from subprocess import check_output as _check_output

from sqlalchemy import create_engine

from tahrir_api.dbapi import TahrirDatabase

from tahrir_api.model import DBSession
from tahrir_api.model import DeclarativeBase

metadata = getattr(DeclarativeBase, 'metadata')


def check_output(cmd):
    try:
        return _check_output(cmd)
    except Exception:  # pragma: no cover
        return None


class BaseTahrirTest(unittest.TestCase):

    def setUp(self):
        check_output(['touch', 'testdb.db'])
        sqlalchemy_uri = "sqlite:///testdb.db"
        engine = create_engine(sqlalchemy_uri)
        DBSession.configure(bind=engine)
        metadata.create_all(engine)

        self.callback_calls = []
        self.api = TahrirDatabase(
            sqlalchemy_uri,
            notification_callback=self.callback
        )

    def tearDown(self):
        check_output(['rm', 'testdb.db'])
        self.callback_calls = []

    def callback(self, *args, **kwargs):
        self.callback_calls.append((args, kwargs))
