# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation API."""

from datetime import timedelta

import ciso8601


def patron_exists(patron_pid):
    """Return True if patron exists, False otherwise."""
    return False


def item_exists(item_pid):
    """Return True if item exists, False otherwise."""
    return False


def is_item_available(item_pid):
    """."""
    return True


def item_resolver(item_pid):
    """Return the item record for the passed item pid."""
    return ""


def item_location_retriever(item_pid):
    """Retrieve the location pid of the passed item pid."""
    return ""


def get_default_loan_duration(loan):
    """Return a default loan duration in number of days."""
    return 30


def get_default_extension_duration(loan):
    """Return a default extension duration in number of days."""
    return 30


def get_default_extension_max_count(loan):
    """Return a default extensions max count."""
    return float("inf")


def is_loan_duration_valid(loan):
    """Validate the loan duration."""
    return loan["end_date"] > loan["start_date"] and loan["end_date"] - loan[
        "start_date"
    ] < timedelta(days=60)


def parse_date(str_date):
    """Parse string date with timezone and return a datetime object."""
    return ciso8601.parse_datetime(str_date)
