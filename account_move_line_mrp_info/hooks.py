# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Link the existing journal items to their manufacturing / unbuild order.

    A journal entry can hold the valuation lines of several stock moves, so
    each line is matched to the moves of its entry by product and reference
    (see stock.move._get_account_move_line_vals), and only linked when that
    match points to a single order.
    """
    _logger.info("Linking existing journal items to manufacturing orders")
    env.cr.execute(
        """
        UPDATE account_move_line aml
        SET mrp_production_id = q.mrp_id
        FROM (
            SELECT aml.id AS aml_id,
                MIN(COALESCE(sm.production_id, sm.raw_material_production_id))
                    AS mrp_id
            FROM account_move_line aml
            JOIN stock_move sm
                ON sm.account_move_id = aml.move_id
                AND sm.product_id = aml.product_id
                AND LEFT(aml.name, LENGTH(sm.reference) + 3) = sm.reference || ' - '
            WHERE COALESCE(sm.production_id, sm.raw_material_production_id)
                IS NOT NULL
            GROUP BY aml.id
            HAVING COUNT(DISTINCT COALESCE(
                sm.production_id, sm.raw_material_production_id)) = 1
        ) q
        WHERE q.aml_id = aml.id
        """
    )
    # Labour cost entries are created per manufacturing order
    env.cr.execute(
        """
        UPDATE account_move_line aml
        SET mrp_production_id = q.mrp_id
        FROM (
            SELECT DISTINCT labour_aml.move_id, wo.production_id AS mrp_id
            FROM mrp_workcenter_productivity wcp
            JOIN mrp_workorder wo ON wo.id = wcp.workorder_id
            JOIN account_move_line labour_aml
                ON labour_aml.id = wcp.account_move_line_id
        ) q
        WHERE q.move_id = aml.move_id AND aml.mrp_production_id IS NULL
        """
    )
    _logger.info("Linking existing journal items to unbuild orders")
    env.cr.execute(
        """
        UPDATE account_move_line aml
        SET unbuild_id = q.unbuild_id
        FROM (
            SELECT aml.id AS aml_id, MIN(sm.unbuild_id) AS unbuild_id
            FROM account_move_line aml
            JOIN stock_move sm
                ON sm.account_move_id = aml.move_id
                AND sm.product_id = aml.product_id
                AND LEFT(aml.name, LENGTH(sm.reference) + 3) = sm.reference || ' - '
            WHERE sm.unbuild_id IS NOT NULL
            GROUP BY aml.id
            HAVING COUNT(DISTINCT sm.unbuild_id) = 1
        ) q
        WHERE q.aml_id = aml.id
        """
    )
