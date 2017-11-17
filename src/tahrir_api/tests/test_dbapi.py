#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_in
from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import instance_of
from hamcrest import starts_with
from hamcrest import has_property
from hamcrest.library.collection.is_empty import empty as is_empty

import six

import fudge

from tahrir_api.dbapi import TahrirDatabase

from tahrir_api.tests import BaseTahrirTest


class TestDBInit(BaseTahrirTest):

    def test_ctor(self):
        with self.assertRaises(ValueError):
            TahrirDatabase()
        with self.assertRaises(ValueError):
            TahrirDatabase('uri', fudge.Fake())

    def test_add_badges(self):
        self.api.add_badge(
            "TestBadge",
            "TestImage",
            "A test badge for doing unit tests",
            "TestCriteria",
            1337
        )

        assert_that(self.api.badge_exists("testbadge"),
                    is_(True))

        assert_that(self.api.delete_badge('xxxx'),
                    is_(False))

        assert_that(self.api.delete_badge('testbadge'),
                    is_('testbadge'))

    def test_add_team(self):
        self.api.create_team("TestTeam")
        assert_that(self.api.team_exists("testteam"), is_(True))

    def test_add_series(self):
        team_id = self.api.create_team("TestTeam")

        self.api.create_series("TestSeries",
                               "A test series",
                               team_id,
                               "test, series")

        assert_that(self.api.series_exists("testseries"), is_(True))

        assert_that(list(self.api.get_all_series()),
                    has_length(1))

    def test_add_milestone(self):
        team_id = self.api.create_team("TestTeam")

        series_id = self.api.create_series("TestSeries",
                                           "A test series",
                                           team_id,
                                           "test, series")

        badge_id_1 = self.api.add_badge(
            "TestBadge-1",
            "TestImage-2",
            "A test badge for doing 10 unit tests",
            "TestCriteria",
            1337
        )

        badge_id_2 = self.api.add_badge(
            "TestBadge-2",
            "TestImage-2",
            "A test badge for doing 100 unit tests",
            "TestCriteria",
            1337
        )

        milestone_id_1 = self.api.create_milestone(1,
                                                   badge_id_1,
                                                   series_id)

        milestone_id_2 = self.api.create_milestone(2,
                                                   badge_id_2,
                                                   series_id)

        assert_that(self.api.milestone_exists(milestone_id_1), is_(True))
        assert_that(self.api.milestone_exists(milestone_id_2), is_(True))

    def test_add_person(self):
        self.api.add_person("test@tester.com", "the_main_tester")
        assert_that(self.api.person_exists("test@tester.com"), is_(True))

        person = self.api.get_person("test@tester.com")
        assert_that(person, is_not(none()))

        person = self.api.get_person(nickname="the_main_tester")
        assert_that(person, is_not(none()))
        person_id = person.id

        person = self.api.get_person(id=person_id)
        assert_that(person, is_not(none()))

        assert_that(self.api.add_person("test@tester.com", "the_main_tester"),
                    is_(False))
        
        assert_that(self.api.person_exists(),
                    is_(False))

        assert_that(self.api.person_opted_out('test2@tester.org'),
                    is_(False))

        assert_that(self.api.person_opted_out('test@tester.com'),
                    is_(False))
        
        assert_that(list(self.api.get_all_persons()),
                    has_length(1))
        
        assert_that(self.api.get_person_email('xxx'),
                    is_(none()))
        
        assert_that(self.api.delete_person('test2@tester.org'),
                    is_(False))
        
        assert_that(self.api.delete_person('test@tester.com'),
                    is_('test@tester.com'))

    def test_add_issuer(self):
        issuer_id = self.api.add_issuer(
            "TestOrigin",
            "TestName",
            "TestOrg",
            "TestContact"
        )
        assert_that(self.api.issuer_exists("TestOrigin", "TestName"),
                    is_(True))
        
        assert_that(self.api.delete_issuer('xxxx'),
                    is_(False))
    
        other_id = self.api.add_issuer(
            "TestOrigin",
            "TestName",
            "TestOrg",
            "TestContact"
        )
        assert_that(other_id, is_(equal_to(issuer_id)))
        
        assert_that(list(self.api.get_all_issuers()),
                    has_length(1))

        assert_that(self.api.delete_issuer(issuer_id),
                    is_(issuer_id))

    def test_add_invitation(self):
        badge_id = self.api.add_badge(
            "TestBadge",
            "TestImage",
            "A test badge for doing unit tests",
            "TestCriteria",
            1337
        )
        _id = self.api.add_invitation(
            badge_id,
        )

        assert_that(self.api.invitation_exists(_id), is_(True))

    def test_last_login(self):
        email = "test@tester.com"
        person_id = self.api.add_person(email)
        person = self.api.get_person(person_id)
        assert_that(person, has_property('last_login', is_(none())))
        self.api.note_login(nickname=person.nickname)
        assert_that(person, has_property('last_login', is_not(none())))

    def test_add_assertion(self):
        issuer_id = self.api.add_issuer(
            "TestOrigin",
            "TestName",
            "TestOrg",
            "TestContact"
        )
        badge_id = self.api.add_badge(
            "TestBadge",
            "TestImage",
            "A test badge for doing unit tests",
            "TestCriteria",
            issuer_id,
        )
        email = "test@tester.com"
        self.api.add_person(email)
        self.api.add_assertion(badge_id, email, None, 'link')
        assert_that(self.api.assertion_exists(badge_id, email), is_(True))

        assert_that(list(self.api.get_all_assertions()),
                    has_length(1))
        
        assert_that(list(self.api.get_assertions_by_email("test@tester.com")),
                    has_length(1))

        assert_that(list(self.api.get_assertions_by_email("test2@tester.org")),
                    is_(is_empty()))

        assert_that(self.api.get_assertions_by_badge('xxx'),
                    is_(is_empty()))

        assert_that(self.api.get_assertions_by_badge(badge_id),
                    is_not(is_empty()))

        badge = self.api.get_badge(badge_id)
        assert_that(badge,
                    has_property('assertions', has_length(1)))
        assertion = badge.assertions[0]
        repr(assertion)  # coverage
        assert_that(assertion,
                    has_property('issued_for', is_('link')))
        assert_that(str(assertion),
                    is_('TestBadge<->test@tester.com'))
        assert_that(assertion,
                    has_property('_recipient', starts_with('sha256$')))

        with self.assertRaises(KeyError):
            assertion['key']
        assert_that(assertion['pygments'],
                    is_(instance_of(six.string_types)))

        # Ensure that we would have published two fedmsg messages for that.
        assert_that(self.callback_calls, has_length(2))

        # Ensure that the first message had a 'badge_id' in the message.
        assert_that('badge_id',
                    is_in(self.callback_calls[0][1]['msg']['badge']))

        assert_that(self.api.assertion_exists(badge_id, "test2@tester.org"),
                    is_(False))
        
        assert_that(self.api.add_assertion('xxxx', "test2@tester.org", None, 'link'),
                    is_(False))

    def test_get_badges_from_tags(self):
        issuer_id = self.api.add_issuer(
            "TestOrigin",
            "TestName",
            "TestOrg",
            "TestContact"
        )

        # Badge tagged with "test"
        self.api.add_badge(
            "TestBadgeA",
            "TestImage",
            "A test badge for doing unit tests",
            "TestCriteria",
            issuer_id,
            tags="test"
        )

        # Badge tagged with "tester"
        self.api.add_badge(
            "TestBadgeB",
            "TestImage",
            "A second test badge for doing unit tests",
            "TestCriteria",
            issuer_id,
            tags="tester"
        )

        # Badge tagged with both "test" and "tester"
        self.api.add_badge(
            "TestBadgeC",
            "TestImage",
            "A third test badge for doing unit tests",
            "TestCriteria",
            issuer_id,
            tags="test, tester"
        )

        tags = ['test', 'tester']
        badges_any = self.api.get_badges_from_tags(tags, match_all=False)
        assert_that(badges_any, has_length(3))
        badges_all = self.api.get_badges_from_tags(tags, match_all=True)
        assert_that(badges_all, has_length(1))
