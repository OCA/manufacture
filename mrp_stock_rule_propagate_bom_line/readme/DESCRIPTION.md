This module adds a Propagate BOM Line checkbox on stock rule.
It provides granular control over how components for kit products are grouped within chained stock moves.

This checkbox is checked by default to align with Odoo's standard behavior.
Component moves are kept separate, preserving the link to their original Bill of Materials (BOM) line.

When the checkbox is unchecked Odoo allows to group the stock moves of the same product if
these stock moves are originating from different kits (ie different BOM
lines).
