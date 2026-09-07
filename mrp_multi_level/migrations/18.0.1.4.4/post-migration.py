# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recompute the main supplier of the MRP parameters.

    ``main_supplierinfo_id`` and ``main_supplier_id`` are stored, but they did
    not depend on the fields of the vendor lines they are computed from. A
    change on an existing vendor line, its company in particular, therefore
    left the stored values pointing to a vendor line that the computation would
    no longer select, and a cross company one breaks every read of the
    parameter for the users of a single company.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    params = env["product.mrp.area"].with_context(active_test=False).search([])
    if not params:
        return
    env.add_to_compute(params._fields["main_supplierinfo_id"], params)
    env.add_to_compute(params._fields["main_supplier_id"], params)
    params.flush_recordset(["main_supplierinfo_id", "main_supplier_id"])
    logger.info("Recomputed the main supplier of %s MRP parameters.", len(params))
