# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Copy `move_dest_id` from the old procurement orders to the new field
    `move_dest_ids` in the Manufacturing Request."""
    cr.execute("""
        SELECT move_dest_id, mrp_production_request_id
        FROM procurement_order
        WHERE mrp_production_request_id is not null;""")
    for move_dest, mrp_request in cr.fetchall():
        if move_dest:
            cr.execute("""
                UPDATE stock_move
                SET created_mrp_production_request_id = %s
                WHERE id = %s
            """, (mrp_request, move_dest,))
