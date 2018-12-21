# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _prepare_mo_vals(self, product_id, product_qty,
                         product_uom, location_id, name,
                         origin, values, bom):

        res = super(ProcurementRule, self)._prepare_mo_vals(product_id,
                                                            product_qty,
                                                            product_uom,
                                                            location_id, name,
                                                            origin, values,
                                                            bom)
        requested_uid = values.get('requested_uid', None)
        if requested_uid:
            res.update({'user_id': requested_uid.id})
        return res
