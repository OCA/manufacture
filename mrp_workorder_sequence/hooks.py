# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


def post_init_hook(cr, registry):
    cr.execute(
        """
            UPDATE mrp_workorder
            SET sequence = n.sequence
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (PARTITION BY production_id) AS sequence
                FROM mrp_workorder
                ORDER BY production_id, id
            ) AS n
            WHERE mrp_workorder.id = n.id
        """
    )
