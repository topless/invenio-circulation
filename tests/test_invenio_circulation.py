# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2019 CERN.
# Copyright (C) 2018-2019 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function


def test_version():
    """Test version import."""
    from invenio_circulation import __version__

    assert __version__
