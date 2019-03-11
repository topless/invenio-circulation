# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""


import ciso8601

from .errors import NotImplementedCirculation


def patron_exists(patron_pid):
    """Return True if patron exists, False otherwise."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_PATRON_EXISTS"
    )


def item_exists(item_pid):
    """Return True if item exists, False otherwise."""
    raise NotImplementedCirculation(config_variable="CIRCULATION_ITEM_EXISTS")


# NOTE: Its on purpose `ref` and not `$ref` so it doesn't try to resolve
def item_ref_builder(loan_pid):
    """Return the $ref for item_pid."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_ITEM_REF_BUILDER"
    )


def item_location_retriever(item_pid):
    """Retrieve the location pid of the passed item pid."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_ITEM_LOCATION_RETRIEVER"
    )


def is_item_available(item_pid):
    """Return if item is available for checkout."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.checkout.is_item_available"
    )


def can_be_requested(loan):
    """Should return True if document or item can be requested."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.request.can_be_requested"
    )


def get_default_loan_duration(loan):
    """Return a default loan duration in number of days."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.checkout.duration_default"
    )


def is_loan_duration_valid(loan):
    """Validate the loan duration."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.checkout.duration_validate"
    )


def get_default_extension_duration(loan):
    """Return a default extension duration in number of days."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.extension.duration_default"
    )


def get_default_extension_max_count(loan):
    """Return a default extensions max count."""
    raise NotImplementedCirculation(
        config_variable="CIRCULATION_POLICIES.extension.max_count"
    )


def parse_date(str_date):
    """Parse string date with timezone and return a datetime object."""
    return ciso8601.parse_datetime(str_date)
