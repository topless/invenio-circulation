# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation views."""

from copy import deepcopy

from flask import Blueprint, current_app, request, url_for
from invenio_db import db
from invenio_records_rest.utils import obj_or_import_string
from invenio_records_rest.views import \
    create_error_handlers as records_rest_error_handlers
from invenio_records_rest.views import pass_record
from invenio_rest import ContentNegotiatedMethodView
from invenio_rest.views import create_api_errorhandler

from invenio_circulation.errors import LoanActionError, \
    NoValidTransitionAvailable
from invenio_circulation.proxies import current_circulation

HTTP_CODES = {
    'method_not_allowed': 405,
    'accepted': 202
}


def create_error_handlers(blueprint):
    """Create error handlers on blueprint."""
    blueprint.errorhandler(LoanActionError)(create_api_errorhandler(
        status=HTTP_CODES['method_not_allowed'], message='Invalid loan action'
    ))
    records_rest_error_handlers(blueprint)


def extract_transitions_from_app(app):
    """."""
    transitions_config = app.config.get('CIRCULATION_LOAN_TRANSITIONS', {})
    distinct_actions = set()
    for src_state, transitions in transitions_config.items():
        for t in transitions:
            distinct_actions.add(t.get('trigger', 'next'))
    return distinct_actions


def build_url_action_for_pid(pid, action):
    """."""
    return url_for(
        'invenio_circulation.{0}_actions'.format(pid.pid_type),
        pid_value=pid.pid_value,
        action=action,
        _external=True
    )


def build_blueprint_with_loan_actions(app):
    """."""
    blueprint = Blueprint(
        'invenio_circulation',
        __name__,
        url_prefix='',
    )
    create_error_handlers(blueprint)

    endpoints = app.config.get('CIRCULATION_REST_ENDPOINTS', [])
    pid_type = 'loan_pid'
    options = endpoints.get(pid_type, {})
    if options:
        options = deepcopy(options)
        serializers = {}
        if 'record_serializers' in options:
            rec_serializers = options.get('record_serializers')
            serializers = {mime: obj_or_import_string(func)
                           for mime, func in rec_serializers.items()}

        loan_actions = LoanActionResource.as_view(
            LoanActionResource.view_name.format(pid_type),
            serializers=serializers,
            ctx=dict(
                links_factory=app.config.get('CIRCULATION_LOAN_LINKS_FACTORY')
            ),
        )

        distinct_actions = extract_transitions_from_app(app)
        url = '{0}/<any({1}):action>'.format(
            options['item_route'],
            ','.join(distinct_actions),
        )

        blueprint.add_url_rule(
            url,
            view_func=loan_actions,
            methods=['POST'],
        )

    return blueprint


class LoanActionResource(ContentNegotiatedMethodView):
    """Loan action resource."""

    view_name = '{0}_actions'

    def __init__(self, serializers, ctx, *args, **kwargs):
        """Constructor."""
        super(LoanActionResource, self).__init__(
            serializers,
            *args,
            **kwargs
        )
        for key, value in ctx.items():
            setattr(self, key, value)

    @pass_record
    def post(self, pid, record, action, **kwargs):
        """Handle loan action."""
        params = request.get_json()
        try:
            # perform action on the current loan
            record = current_circulation.circulation.trigger(
                record, **dict(params, trigger=action)
            )
            db.session.commit()
        except NoValidTransitionAvailable as ex:
            current_app.logger.exception(ex.msg)
            raise LoanActionError(ex)

        return self.make_response(
            pid, record, HTTP_CODES['accepted'],
            links_factory=self.links_factory
        )
