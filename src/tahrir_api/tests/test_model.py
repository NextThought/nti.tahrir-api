#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries

import fudge

from tahrir_api.model import generate_default_id

from tahrir_api.tests import BaseTahrirTest


class TestModel(BaseTahrirTest):

    def test_issuer(self):
        issuer = self.api.get_issuer('xyz')
        assert_that(issuer, is_(none()))

        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        issuer = self.api.get_issuer(issuer_id)
        repr(issuer)

        assert_that(str(issuer), is_('aizen'))
        assert_that(issuer.__json__(),
                    has_entries('origin', 'http://bleach.org',
                                'org', 'Bleach',
                                'created_on', is_(float),
                                'contact', 'aizen@bleach.org',
                                'name', u'aizen'))

    def test_generate_default_id(self):
        params = {'name': 'my id'}
        context = fudge.Fake().has_attr(current_parameters=params)
        assert_that(generate_default_id(context),
                    is_('my-id'))

    def test_badge(self):
        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        badge = self.api.get_badge('kido')
        assert_that(badge, is_(none()))

        badge_id = self.api.add_badge(
            "kido",
            "kido",
            "A test badge for doing kido",
            "kido-expert",
            issuer_id,
        )
        badge = self.api.get_badge(badge_id)
        repr(badge)

        assert_that(str(badge), is_('kido'))

        assert_that(badge.__json__(),
                    has_entries('name', 'kido',
                                'tags', is_(none()),
                                'image', '/pngs/kido',
                                'description', 'A test badge for doing kido',
                                'created_on', is_(float),
                                'version', '0.5.0',
                                'criteria', 'kido-expert',
                                'issuer', is_(dict)))

        self.api.add_person('hinamori@bleach.org', 'hinamori',
                            "http://bleach.org", 'lieutenant of the 5th Division')

        self.api.add_authorization(badge_id, 'hinamori@bleach.org')

        # get badge due to autocommit
        badge = self.api.get_badge(badge_id)
        assert_that(badge.authorized('izuru@bleach.org'),
                    is_(False))
        person = self.api.get_person('hinamori@bleach.org')
        assert_that(badge.authorized(person),
                    is_(True))

    def test_team_series_milestone(self):
        assert_that(self.api.get_team('bankai'), is_(none()))
        team_id = self.api.create_team('bankai')
        team = self.api.get_team(team_id)
        assert_that(team, is_not(none()))
        repr(team)

        assert_that(str(team), is_('bankai'))
        assert_that(team.__json__(),
                    has_entries('id', team_id,
                                'name', 'bankai',
                                'created_on', is_not(none())))

        assert_that(self.api.get_series('bleach'), is_(none()))
        series_id = self.api.create_series('bleach', 'anime',
                                           team_id, 'japan')
        series = self.api.get_series(series_id)
        assert_that(series, is_not(none()))
        repr(series)

        assert_that(str(series), is_('bleach'))
        assert_that(series.__json__(),
                    has_entries('id', series_id,
                                'name', 'bleach',
                                'created_on', is_not(none()),
                                'last_updated', is_not(none()),
                                'team', is_(dict)))

        assert_that(self.api.get_series_from_team('bleach'),
                    is_(none()))

        assert_that(self.api.get_series_from_team('bankai'),
                    is_not(none()))

        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        badge = self.api.get_badge('materialize')
        assert_that(badge, is_(none()))

        badge_id = self.api.add_badge(
            "materialize",
            "materialize",
            "subjugate zanpakuto",
            "summon the zanpakuto's spirit into the physical world.",
            issuer_id,
        )
        assert_that(self.api.milestone_exists('10years'), is_(False))
        assert_that(self.api.get_milestone('10years'), is_(none()))

        mil_id = self.api.create_milestone(1, badge_id, series_id)
        milestone = self.api.get_milestone(mil_id)
        repr(milestone)

        assert_that(milestone.__json__(),
                    has_entries('position', 1,
                                'series_id', series_id,
                                'badge', is_(dict)))

        assert_that(self.api.get_all_milestones(series_id),
                    has_length(1))

        assert_that(self.api.milestone_exists_for_badge_series(badge_id, series_id),
                    is_(True))

        assert_that(self.api.get_milestone_from_badge_series(badge_id, series_id),
                    is_not(none()))
