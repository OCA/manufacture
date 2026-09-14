This module extends the functionality of Manufacturing Orders to support
the OCA `base_exception` framework.

It allows you to define customizable, logic-driven rules (exceptions)
that can halt the progression of a Manufacturing Order (MO). When a user
attempts to mark an MO as done, the system evaluates it against active
exception rules. If any rules are triggered, the user is blocked from
completing the order until the underlying issue is resolved or an
authorized manager explicitly ignores the exception.
