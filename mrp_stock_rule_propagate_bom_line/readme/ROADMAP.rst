Since version 15.0, Odoo propagates `bom_line_id` from the move to the procurement
in any case.

Therefore, if this module is to be migrated, it must provide the checkbox on the stock
rule to remove the propagation and allow merging of the moves.
