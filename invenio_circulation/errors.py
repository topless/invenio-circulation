# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation exceptions."""

import json

from flask import current_app
from invenio_rest.errors import RESTException


class CirculationException(RESTException):
    """Base Exception for circulation module, inherit, don't raise."""

    code = 400

    @property
    def name(self):
        """The status name."""
        return type(self).__name__

    def __init__(self, **kwargs):
        """Initialize exception."""
        super(CirculationException, self).__init__(**kwargs)

    def get_response(self, environ=None, **kwargs):
        """Intercept response to add info and log the error."""
        resp = super(CirculationException, self).get_response(environ=environ)
        data = json.loads(resp.data.decode('utf-8'))
        data["error_module"] = "Circulation"
        data["error_class"] = self.name
        resp.data = json.dumps(data)
        current_app.logger.exception(self)
        return resp


# Permissions
class InvalidPermission(CirculationException):
    """Raised when permissions are not satisfied for transition."""

    code = 403

    def __init__(self, action=None, permission=None, **kwargs):
        """Initialize exception."""
        super(InvalidPermission, self).__init__(**kwargs)
        self.description = "The action '{0}' is not permitted " \
            "for your role '{1}'".format(action, permission)


# Transitions
class TransitionConstraintsViolation(CirculationException):
    """Exception raised when constraints for the transition failed."""

    description = "Transition constraints have been wildly violated."


class TransitionConditionsFailed(CirculationException):
    """Conditions for the transition failed at loan state."""

    description = "Transition conditions have failed."


class NoValidTransitionAvailable(CirculationException):
    """Exception raised when all transitions conditions failed."""

    def __init__(self, loan_pid=None, state=None, **kwargs):
        """Initialize exception."""
        super(NoValidTransitionAvailable, self).__init__(**kwargs)
        self.description = (
            "For the loan with pid '{0}' there are no valid transitions from "
            "its current state '{1}'".format(loan_pid, state)
        )


# Loans
class InvalidLoanState(CirculationException):
    """State not found in circulation configuration."""

    def __init__(self, state=None, **kwargs):
        """Initialize exception."""
        self.description = "Invalid loan state '{}'".format(state)
        super(InvalidLoanState, self).__init__(**kwargs)


class ItemNotAvailable(CirculationException):
    """Exception raised from action on unavailable item."""

    def __init__(self, item_pid=None, transition=None, **kwargs):
        """Initialize exception."""
        super(ItemNotAvailable, self).__init__(**kwargs)
        self.description = (
            "The item requested with pid '{0}' is not available. "
            "Transition to '{1}' has failed.".format(item_pid, transition)
        )


class ItemDoNotMatch(CirculationException):
    """Exception raised from action on unavailable item."""


class MultipleLoansOnItem(CirculationException):
    """Exception raised when more than one loan on an item."""

    def __init__(self, item_pid=None, **kwargs):
        """Initialize exception."""
        super(MultipleLoansOnItem, self).__init__(**kwargs)
        self.description = (
            "Multiple active loans on item with pid '{}'".format(item_pid)
        )


class LoanMaxExtension(CirculationException):
    """Exception raised when reached the max extensions for a loan."""

    def __init__(self, loan_pid=None, extension_count=None, **kwargs):
        """Initialize exception."""
        super(LoanMaxExtension, self).__init__(**kwargs)
        self.description = (
            "You have reached the maximum amount of extesions '{}' "
            "for loan '{}'".format(extension_count, loan_pid)
        )


# General
class RecordCannotBeRequested(CirculationException):
    """Exception raised when item can not be requested."""


class NotImplementedCirculation(CirculationException):
    """Exception raised when function is not implemented."""

    description = (
        "Function is not implemented. Implement this function in your module "
        "and pass it to the config variable"
    )

    def __init__(self, config_variable=None, **kwargs):
        """Initialize exception."""
        super(NotImplementedCirculation, self).__init__(**kwargs)
        self.description = "{} '{}'".format(self.description, config_variable)


class PropertyRequired(CirculationException):
    """Exception raised when property is not defined."""
