# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2018 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

import pytest

from hypothesistooling.releasemanagement import bump_version_info, \
    release_date_string, update_markdown_changelog, \
    parse_release_file_contents
from hypothesistooling.releasemanagement import \
    replace_assignment_in_string as replace


def parse_release(contents):
    return parse_release_file_contents(contents, '<string>')


def test_update_single_line():
    assert replace('a = 1', 'a', '2') == 'a = 2'


def test_update_without_spaces():
    assert replace('a=1', 'a', '2') == 'a=2'


def test_update_in_middle():
    assert replace('a = 1\nb=2\nc = 3', 'b', '4') == 'a = 1\nb=4\nc = 3'


def test_quotes_string_to_assign():
    assert replace('a.c = 1', 'a.c', '2') == 'a.c = 2'
    with pytest.raises(ValueError):
        replace('abc = 1', 'a.c', '2')


def test_duplicates_are_errors():
    with pytest.raises(ValueError):
        replace('a = 1\na=1', 'a', '2')


def test_missing_is_error():
    with pytest.raises(ValueError):
        replace('', 'a', '1')


def test_bump_minor_version():
    assert bump_version_info((1, 1, 1), 'minor')[0] == '1.2.0'


def test_parse_release_file():
    assert parse_release('RELEASE_TYPE: patch\nhi') == ('patch', 'hi')
    assert parse_release('RELEASE_TYPE: minor\n\n\n\nhi') == \
        ('minor', 'hi')
    assert parse_release('RELEASE_TYPE: major\n \n\nhi') == \
        ('major', 'hi')


def test_invalid_release():
    with pytest.raises(ValueError):
        parse_release('RELEASE_TYPE: wrong\nstuff')

    with pytest.raises(ValueError):
        parse_release('')


TEST_CHANGELOG = """
# A test project 1.2.3 (%s)

some stuff happened

# some previous log entry
""" % (release_date_string(),)


def test_update_changelog(tmpdir):
    path = tmpdir.join('CHANGELOG.md')
    path.write('# some previous log entry\n')
    update_markdown_changelog(
        str(path), 'A test project', '1.2.3', 'some stuff happened'
    )
    assert path.read().strip() == TEST_CHANGELOG.strip()


def test_changelog_parsing_strips_trailing_whitespace():
    header = 'RELEASE_TYPE: patch\n\n'
    contents = 'Adds a feature\n    indented.\n'
    level, out = parse_release(
        header + contents.replace('feature', 'feature    ')
    )
    assert contents.strip() == out
