# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Circulation custom transitions."""

from datetime import timedelta

from flask import current_app
from invenio_db import db

from ..api import can_be_requested, get_available_item_by_doc_pid, \
    get_document_by_item_pid, get_pending_loans_by_doc_pid
from ..errors import LoanMaxExtension, RecordCannotBeRequested, \
    TransitionConditionsFailed, TransitionConstraintsViolation
from ..transitions.base import Transition
from ..transitions.conditions import is_same_location
from ..utils import parse_date


def _ensure_valid_loan_duration(loan):
    """Validate start and end dates for a loan."""
    loan.setdefault('start_date', loan['transaction_date'])

    if not loan.get('end_date'):
        get_loan_duration = current_app.config['CIRCULATION_POLICIES'][
            'checkout']['duration_default']
        number_of_days = get_loan_duration(loan)
        loan['end_date'] = loan['start_date'] + timedelta(days=number_of_days)

    is_duration_valid = current_app.config['CIRCULATION_POLICIES']['checkout'][
        'duration_validate']
    if not is_duration_valid(loan):
        msg = "The loan duration from '{0}' to '{1}' is not valid.".format(
            loan['start_date'],
            loan['end_date']
        )
        raise TransitionConstraintsViolation(description=msg)


def _ensure_item_attached_to_loan(loan):
    """Validate that an item is attached to a loan."""
    if not loan.get('item_pid'):
        msg = "No item attached in loan with pid '{0}'.".format(loan.id)
        raise TransitionConditionsFailed(description=msg)


def _update_document_pending_request_for_item(item_pid):
    """."""
    document_pid = get_document_by_item_pid(item_pid)
    for loan in get_pending_loans_by_doc_pid(document_pid):
        loan['item_pid'] = item_pid
        loan.commit()
        db.session.commit()
        # TODO: index loan again?


def _ensure_valid_extension(loan):
    """Validate end dates for a extended loan."""
    get_extension_max_count = current_app.config['CIRCULATION_POLICIES'][
        'extension']['max_count']
    extension_max_count = get_extension_max_count(loan)

    extension_count = loan.get('extension_count', 0)
    extension_count += 1

    if extension_count > extension_max_count:
        raise LoanMaxExtension(
            loan_pid=loan["loan_pid"],
            extension_count=extension_max_count
        )

    loan['extension_count'] = extension_count

    get_extension_duration = current_app.config['CIRCULATION_POLICIES'][
        'extension']['duration_default']
    number_of_days = get_extension_duration(loan)
    get_extension_from_end_date = current_app.config[
        'CIRCULATION_POLICIES']['extension']['from_end_date']

    end_date = parse_date(loan['end_date'])
    if not get_extension_from_end_date:
        end_date = loan.get('transaction_date')

    end_date += timedelta(days=number_of_days)
    loan['end_date'] = end_date.isoformat()


class ToItemOnLoan(Transition):
    """Action to checkout."""

    def before(self, loan, **kwargs):
        """Validate checkout action."""
        super(ToItemOnLoan, self).before(loan, **kwargs)

        self.ensure_item_is_available(loan)

        if loan.get('start_date'):
            loan['start_date'] = parse_date(loan['start_date'])
        if loan.get('end_date'):
            loan['end_date'] = parse_date(loan['end_date'])

        _ensure_valid_loan_duration(loan)

    def after(self, loan):
        """Convert dates to string before saving loan."""
        loan['start_date'] = loan['start_date'].isoformat()
        loan['end_date'] = loan['end_date'].isoformat()
        super(ToItemOnLoan, self).after(loan)


class ItemAtDeskToItemOnLoan(ToItemOnLoan):
    """Check-out action to perform a loan when item ready at desk."""

    def before(self, loan, **kwargs):
        """Validate checkout action."""
        super(ToItemOnLoan, self).before(loan, **kwargs)

        if loan.get('start_date'):
            loan['start_date'] = parse_date(loan['start_date'])

        if loan.get('end_date'):
            loan['end_date'] = parse_date(loan['end_date'])

        _ensure_valid_loan_duration(loan)


class CreatedToPending(Transition):
    """Action to request to loan an item."""

    def check_request_on_document(f):
        """Decorate to check if the request is on document."""
        def inner(self, loan, **kwargs):
            document_pid = kwargs.get('document_pid')
            if document_pid and not kwargs.get('item_pid'):
                if not can_be_requested(loan):
                    msg = (
                        'Transition to {0} failed.'
                        'Document {1} can not be requested.'
                    ).format(self.dest, loan.get('document_pid'))
                    raise RecordCannotBeRequested(description=msg)

                available_item_pid = get_available_item_by_doc_pid(
                    document_pid
                )
                if available_item_pid:
                    kwargs['item_pid'] = available_item_pid
            return f(self, loan, **kwargs)
        return inner

    @check_request_on_document
    def before(self, loan, **kwargs):
        """Set a default pickup location if not passed as param."""
        super(CreatedToPending, self).before(loan, **kwargs)

        if not can_be_requested(loan):
            msg = (
                'Transition to {0} failed. Item {1} can not be requested.'
            ).format(self.dest, loan.get('item_pid'))
            raise RecordCannotBeRequested(description=msg)

        # set pickup location to item location if not passed as default
        if not loan.get('pickup_location_pid'):
            item_location_pid = current_app.config[
                'CIRCULATION_ITEM_LOCATION_RETRIEVER'](loan['item_pid'])
            loan['pickup_location_pid'] = item_location_pid


class PendingToItemAtDesk(Transition):
    """Validate pending request to prepare the item at desk of its location."""

    def before(self, loan, **kwargs):
        """Validate if the item is for this location or should transit."""
        super(PendingToItemAtDesk, self).before(loan, **kwargs)

        # check if a request on document has no item attached
        _ensure_item_attached_to_loan(loan)

        if not is_same_location(loan['item_pid'], loan['pickup_location_pid']):
            msg = "Pickup is not at the same library. " \
                "Transition to {} has failed.".format(self.dest)
            raise TransitionConditionsFailed(description=msg)


class PendingToItemInTransitPickup(Transition):
    """Validate pending request to send the item to the pickup location."""

    def before(self, loan, **kwargs):
        """Validate if the item is for this location or should transit."""
        super(PendingToItemInTransitPickup, self).before(loan, **kwargs)

        # check if a request on document has no item attached
        _ensure_item_attached_to_loan(loan)

        if is_same_location(loan['item_pid'], loan['pickup_location_pid']):
            msg = "Pickup is at the same library. " \
                "Transition to '{0}' has failed.".format(self.dest)
            raise TransitionConditionsFailed(description=msg)


class ItemOnLoanToItemOnLoan(Transition):
    """Extend action to perform a item loan extension."""

    def before(self, loan, **kwargs):
        """Validate extension action."""
        super(ItemOnLoanToItemOnLoan, self).before(loan, **kwargs)
        _ensure_valid_extension(loan)


class ItemOnLoanToItemInTransitHouse(Transition):
    """Check-in action when returning an item not to its belonging location."""

    def before(self, loan, **kwargs):
        """Validate check-in action."""
        super(ItemOnLoanToItemInTransitHouse, self).before(loan, **kwargs)
        if is_same_location(loan['item_pid'],
                            loan['transaction_location_pid']):
            msg = "Item should be returned (already in house). " \
                "Transition to '{0}' has failed.".format(self.dest)
            raise TransitionConditionsFailed(description=msg)

        # set end loan date as transaction date when completing loan
        loan['end_date'] = loan['transaction_date']

    def after(self, loan):
        """Convert dates to string before saving loan."""
        loan['end_date'] = loan['end_date'].isoformat()
        super(ItemOnLoanToItemInTransitHouse, self).after(loan)


class ItemOnLoanToItemReturned(Transition):
    """Check-in action when returning an item to its belonging location."""

    def before(self, loan, **kwargs):
        """Validate check-in action."""
        super(ItemOnLoanToItemReturned, self).before(loan, **kwargs)
        if not is_same_location(loan['item_pid'],
                                loan['transaction_location_pid']):
            msg = "Item should be in transit to house. " \
                "Transition to '{0}' has failed.".format(self.dest)
            raise TransitionConditionsFailed(description=msg)

        # set end loan date as transaction date when completing loan
        loan['end_date'] = loan['transaction_date']

    def after(self, loan):
        """Convert dates to string before saving loan."""
        loan['end_date'] = loan['end_date'].isoformat()
        super(ItemOnLoanToItemReturned, self).after(loan)
        _update_document_pending_request_for_item(loan['item_pid'])


class ItemInTransitHouseToItemReturned(Transition):
    """Check-in action when returning an item to its belonging location."""

    def after(self, loan):
        """Convert dates to string before saving loan."""
        super(ItemInTransitHouseToItemReturned, self).after(loan)
        _update_document_pending_request_for_item(loan['item_pid'])
