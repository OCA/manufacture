With Odoo's standard workflow, when using the subcontracting operation
type and assigning serial numbers via **Mass Produce** on a subcontracting
MO with serial-tracked finished products, the system assigns serials but
does not automatically record components.

This is problematic because when receiving multiple quantities, users
need to assign serials at once to reduce operation time. Without
automatic component recording, users must manually open and record
components for each individual MO, which is time-consuming.

This module solves this by:

* Automatically recording components for all MOs when Mass Produce is used
* Adding a **Mass Produce** button to the "Record Components" form for easier access
