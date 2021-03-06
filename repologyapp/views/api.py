#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import json

import flask

from repologyapp.globals import *
from repologyapp.metapackages import bound_to_filter
from repologyapp.view_registry import ViewRegistrar

from repology.config import config
from repology.metapackageproc import PackagesToMetapackages
from repology.queryfilters import *


def api_v1_package_to_json(package):
    output = {
        field: getattr(package, field) for field in (
            'repo',
            'subrepo',
            'name',
            'version',
            'origversion',
            'maintainers',
            #'category',
            #'comment',
            #'homepage',
            'licenses',
            'downloads'
        ) if getattr(package, field)
    }

    # XXX: these tweaks should be implemented in core
    if package.homepage:
        output['www'] = [package.homepage]
    if package.comment:
        output['summary'] = package.comment
    if package.category:
        output['categories'] = [package.category]

    return output


def api_v1_metapackages_generic(bound, *filters):
    metapackages = PackagesToMetapackages(
        get_db().GetMetapackages(
            bound_to_filter(bound),
            *filters,
            limit=config['METAPACKAGES_PER_PAGE']
        )
    )

    metapackages = {metapackage_name: list(map(api_v1_package_to_json, packageset)) for metapackage_name, packageset in metapackages.items()}

    return (
        json.dumps(metapackages),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api')
@ViewRegistrar('/api/v1')
def api_v1():
    return flask.render_template('api.html', per_page=config['METAPACKAGES_PER_PAGE'])


@ViewRegistrar('/api/v1/metapackage/<name>')
def api_v1_metapackage(name):
    return (
        json.dumps(list(map(
            api_v1_package_to_json,
            get_db().GetMetapackage(name)
        ))),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/v1/metapackages/')
@ViewRegistrar('/api/v1/metapackages/all/')
@ViewRegistrar('/api/v1/metapackages/all/<bound>/')
def api_v1_metapackages_all(bound=None):
    return api_v1_metapackages_generic(bound)


@ViewRegistrar('/api/v1/metapackages/unique/')
@ViewRegistrar('/api/v1/metapackages/unique/<bound>/')
def api_v1_metapackages_unique(bound=None):
    return api_v1_metapackages_generic(bound, InNumFamiliesQueryFilter(less=1))


@ViewRegistrar('/api/v1/metapackages/in-repo/<repo>/')
@ViewRegistrar('/api/v1/metapackages/in-repo/<repo>/<bound>/')
def api_v1_metapackages_in_repo(repo, bound=None):
    return api_v1_metapackages_generic(bound, InRepoQueryFilter(repo))


@ViewRegistrar('/api/v1/metapackages/outdated-in-repo/<repo>/')
@ViewRegistrar('/api/v1/metapackages/outdated-in-repo/<repo>/<bound>/')
def api_v1_metapackages_outdated_in_repo(repo, bound=None):
    return api_v1_metapackages_generic(bound, OutdatedInRepoQueryFilter(repo))


@ViewRegistrar('/api/v1/metapackages/not-in-repo/<repo>/')
@ViewRegistrar('/api/v1/metapackages/not-in-repo/<repo>/<bound>/')
def api_v1_metapackages_not_in_repo(repo, bound=None):
    return api_v1_metapackages_generic(bound, NotInRepoQueryFilter(repo))


@ViewRegistrar('/api/v1/metapackages/candidates-in-repo/<repo>/')
@ViewRegistrar('/api/v1/metapackages/candidates-in-repo/<repo>/<bound>/')
def api_v1_metapackages_candidates_in_repo(repo, bound=None):
    return api_v1_metapackages_generic(bound, NotInRepoQueryFilter(repo), InNumFamiliesQueryFilter(more=5))


@ViewRegistrar('/api/v1/metapackages/unique-in-repo/<repo>/')
@ViewRegistrar('/api/v1/metapackages/unique-in-repo/<repo>/<bound>/')
def api_v1_metapackages_unique_in_repo(repo, bound=None):
    return api_v1_metapackages_generic(bound, InNumFamiliesQueryFilter(less=1))


@ViewRegistrar('/api/v1/metapackages/by-maintainer/<maintainer>/')
@ViewRegistrar('/api/v1/metapackages/by-maintainer/<maintainer>/<bound>/')
def api_v1_metapackages_by_maintainer(maintainer, bound=None):
    return api_v1_metapackages_generic(bound, MaintainerQueryFilter(maintainer))


@ViewRegistrar('/api/v1/metapackages/outdated-by-maintainer/<maintainer>/')
@ViewRegistrar('/api/v1/metapackages/outdated-by-maintainer/<maintainer>/<bound>/')
def api_v1_metapackages_outdated_by_maintainer(maintainer, bound=None):
    return api_v1_metapackages_generic(bound, MaintainerOutdatedQueryFilter(maintainer))


@ViewRegistrar('/api/v1/repository/<repo>/problems')
def api_v1_repository_problems(repo):
    return (
        json.dumps(get_db().GetProblems(repo=repo)),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/v1/maintainer/<maintainer>/problems')
def api_v1_maintainer_problems(maintainer):
    return (
        json.dumps(get_db().GetProblems(maintainer=maintainer)),
        {'Content-type': 'application/json'}
    )


#@ViewRegistrar('/api/v1/history/repository/<repo>')
#def api_v1_maintainer_problems():
#    get_db().GetRepositoriesHistoryPeriod(seconds = 365
#    return (
#        json.dumps(get_db().GetProblems(maintainer=maintainer)),
#        {'Content-type': 'application/json'}
#    )


#@ViewRegistrar('/api/v1/history/statistics')
#def api_v1_maintainer_problems(repo):
#    return (
#        json.dumps(get_db().GetProblems(maintainer=maintainer)),
#        {'Content-type': 'application/json'}
#    )
