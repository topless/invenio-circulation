# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation exceptions."""

import json
from enum import Enum

from flask import current_app
from invenio_rest.errors import RESTException


class ErrorCodes(Enum):
    """Circulation error codes."""

    # Permissions
    INVALID_PERMISSION = 10

    # Transitions
    TRANSITION_CONSTRAINTS_VIOLATION = 20
    TRANSITION_CONDITIONS_FAILED = 21
    NO_VALID_TRANSITION_AVAILABLE = 22

    # Loan
    INVALID_LOAN_STATE = 30
    ITEM_NOT_AVAILABLE = 31
    ITEM_DO_NOT_MATCH = 32
    MULTIPLE_LOANS_ON_ITEM = 33
    LOAN_MAX_EXTENSION = 34

    # General
    NOT_IMPLEMENTED_CIRCULATION = 40
    RECORD_CANNOT_BE_REQUESTED = 41
    PROPERTY_REQUIRED = 42


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
        if hasattr(self, 'circulation_code'):
            data = json.loads(resp.data.decode('utf-8'))
            data['circulation_code'] = self.circulation_code
            data['circulation_error'] = self.name
            resp.data = json.dumps(data)
        current_app.logger.exception(self)
        return resp


# Permissions
class InvalidPermission(CirculationException):
    """Raised when permissions are not satisfied for transition."""

    code = 403
    circulation_code = ErrorCodes.INVALID_PERMISSION.value

    def __init__(self, action=None, permission=None, **kwargs):
        """Initialize exception."""
        super(InvalidPermission, self).__init__(**kwargs)
        self.description = "The action '{0}' is not permitted " \
            "for your role '{1}'".format(action, permission)


# Transitions
class TransitionConstraintsViolation(CirculationException):
    """Exception raised when constraints for the transition failed."""

    circulation_code = ErrorCodes.TRANSITION_CONSTRAINTS_VIOLATION.value
    description = "Transition constraints have been wildly violated."


class TransitionConditionsFailed(CirculationException):
    """Conditions for the transition failed at loan state."""

    circulation_code = ErrorCodes.TRANSITION_CONDITIONS_FAILED.value
    description = "Transition conditions have failed."


class NoValidTransitionAvailable(CirculationException):
    """Exception raised when all transitions conditions failed."""

    circulation_code = ErrorCodes.NO_VALID_TRANSITION_AVAILABLE.value

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

    circulation_code = ErrorCodes.INVALID_LOAN_STATE.value

    def __init__(self, state=None, **kwargs):
        """Initialize exception."""
        self.description = "Invalid loan state '{}'".format(state)
        super(InvalidLoanState, self).__init__(**kwargs)


class ItemNotAvailable(CirculationException):
    """Exception raised from action on unavailable item."""

    circulation_code = ErrorCodes.ITEM_NOT_AVAILABLE.value

    def __init__(self, item_pid=None, transition=None, **kwargs):
        """Initialize exception."""
        super(ItemNotAvailable, self).__init__(**kwargs)
        self.description = (
            "The item requested with pid '{0}' is not available. "
            "Transition to '{1}' has failed.".format(item_pid, transition)
        )


class ItemDoNotMatch(CirculationException):
    """Exception raised from action on unavailable item."""

    circulation_code = ErrorCodes.ITEM_DO_NOT_MATCH.value


class MultipleLoansOnItem(CirculationException):
    """Exception raised when more than one loan on an item."""

    circulation_code = ErrorCodes.MULTIPLE_LOANS_ON_ITEM.value

    def __init__(self, item_pid=None, **kwargs):
        """Initialize exception."""
        super(MultipleLoansOnItem, self).__init__(**kwargs)
        self.description = (
            "Multiple active loans on item with pid '{}'".format(item_pid)
        )


class LoanMaxExtension(CirculationException):
    """Exception raised when reached the max extensions for a loan."""

    circulation_code = ErrorCodes.LOAN_MAX_EXTENSION.value

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

    circulation_code = ErrorCodes.RECORD_CANNOT_BE_REQUESTED.value


class NotImplementedCirculation(CirculationException):
    """Exception raised when function is not implemented."""

    circulation_code = ErrorCodes.NOT_IMPLEMENTED_CIRCULATION.value
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

    circulation_code = ErrorCodes.PROPERTY_REQUIRED.value
