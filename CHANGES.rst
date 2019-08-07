..
    Copyright (C) 2018 CERN.
    Copyright (C) 2018 RERO.
    Invenio-Circulation is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 1.0.0a15 (released 2019-08-07)

- remove ES 2 support
- change `loan_pid` to `pid` schema field

Version 1.0.0a14 (released 2019-06-24)

- now allows loans to be created solely on document_pid
- refactored and added more tests for transitions

Version 1.0.0a13 (released 2019-04-24)

- fixed item reference attachment on checkout

Version 1.0.0a12 (released 2019-04-17)

- Renamed is_item_available circulation policy to item_can_circulate.

Version 1.0.0a11 (released 2019-03-29)

- Add sort options to search api

Version 1.0.0a10 (released 2019-03-27)

- Fix for permissions check


Version 1.0.0a9 (released 2019-03-25)

- Introduce Circulation Exceptions

Version 1.0.0a8 (released 2019-03-06)

- Introduce `request` policy.
- Pass previous loan and trigger name on the state change signal.

Version 1.0.0a7 (released 2019-02-25)

- Replace item_pid with loan_pid in $ref Loan schema.

Version 1.0.0a6 (released 2019-02-04)

- Force user to implement configuration utils functions instead of returning a
  dummy value.

Version 1.0.0a5 (released 2019-01-28)

- Add config for defining loan `completed` state.

Version 1.0.0a4 (released 2019-01-26)

- Loan replace item endpoint.

Version 1.0.0a3 (released 2019-01-18)

- Creating item reference only when item pid is attached.

Version 1.0.0a2 (released 2019-01-18)

- Adding support for creating a reference inside `Loan` record to an item.

Version 1.0.0a1 (released 2018-12-04)

- Initial public release.
