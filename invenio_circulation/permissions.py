# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2019 CERN.
#
# invenio-circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation permissions."""

from __future__ import absolute_import, print_function

from functools import wraps

from flask import abort, current_app
from flask_login import current_user
from invenio_access import action_factory
from invenio_access.permissions import Permission
from invenio_records_rest.utils import allow_all

loan_read_access = action_factory('loan-read-access')


def check_permission(permission):
    """Abort if permission is not allowed.

    :param permission: The permission to check.
    """
    # NOTE: we have to explicitly check for not None, since flask-principal
    # overrides the default __bool__ implementation for permission.
    if permission is not None and not permission.can():
        if not current_user.is_authenticated:
            abort(401)
        abort(403)


def has_read_loan_permission(*args, **kwargs):
    """Return permission to allow user to access loan."""
    return Permission(loan_read_access)


def views_permissions_factory(action):
    """Circulation views permissions factory."""
    if action == 'loan-read-access':
        return allow_all()
    elif action == 'loan-actions':
        return allow_all()


def need_permissions(action):
    """View decorator to check permissions for the given action or abort.

    :param action: The action to evaluate permissions.
    """
    def decorator_builder(f):
        @wraps(f)
        def decorate(*args, **kwargs):
            check_permission(
                current_app
                .config['CIRCULATION_VIEWS_PERMISSIONS_FACTORY'](action)
            )
            return f(*args, **kwargs)
        return decorate
    return decorator_builder
