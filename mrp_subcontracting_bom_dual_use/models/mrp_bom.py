# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    allow_in_regular_production = fields.Boolean(string="Allow in regular production")

    @api.constrains("operation_ids", "type", "allow_in_regular_production")
    def _check_subcontracting_no_operation(self):
        """Prevent ValidationError if 'Allow in regular production' is checked"""
        domain = [
            ("type", "=", "subcontract"),
            ("allow_in_regular_production", "=", False),
            ("operation_ids", "!=", False),
        ]
        if self.filtered_domain(domain):
            super()._check_subcontracting_no_operation()
        return False

    @api.model
    def _bom_find_domain(
        self,
        product_tmpl=None,
        product=None,
        picking_type=None,
        company_id=False,
        bom_type=False,
    ):
        """We need to overwrite the domain to get subcontract boms"""
        domain = super()._bom_find_domain(
            product_tmpl=product_tmpl,
            product=product,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        if bom_type == "normal":
            domain_old = ("type", "=", "normal")
            domain_new = [
                "|",
                domain_old,
                "&",
                ("type", "=", "subcontract"),
                ("allow_in_regular_production", "=", True),
            ]
            index = domain.index(domain_old)
            domain = domain[:index] + domain_new + domain[index + 1 :]
        return domain
