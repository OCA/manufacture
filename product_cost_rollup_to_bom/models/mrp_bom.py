# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    std_cost_update_date = fields.Datetime(
        string="Standard Cost Update Date",
        copy=False,
        help="Last time the standard cost was performed on this BOM.",
    )

    def get_product_variants(self, product):
        # Returns all the Variants for the requested product
        return product.with_prefetch().product_variant_ids

    def _update_bom(self, bomdate):
        self.ensure_one()
        for line in self.bom_line_ids:
            if line.child_bom_id:
                result = line.child_bom_id._update_bom(self.std_cost_update_date)
                if result:
                    return True
            elif (
                not line.product_id.std_cost_update_date
                or not self.std_cost_update_date
                or line.product_id.std_cost_update_date > self.std_cost_update_date
                or line.product_id.write_date > self.std_cost_update_date
                or line.product_id.product_tmpl_id.write_date
                > self.std_cost_update_date
                or (bomdate and line.product_id.write_date > bomdate)
            ):
                return True
        return False

    @api.model
    def compute_bom_cost_rollup(self):

        _logger.info("BOM Cost Rollup Process Started")

        # Get BoM's whose product is using costing method as standard
        current_time = datetime.now()

        bom_ids = self.sudo().search(
            [("product_tmpl_id.categ_id.property_cost_method", "=", "standard")]
        )
        for bom in bom_ids:
            # Check if cost method is standard
            if (
                bom.product_tmpl_id.categ_id.property_cost_method
                and bom.product_tmpl_id.categ_id.property_cost_method == "standard"
            ):
                # Get all product variants for BoM product template
                product_variants = self.get_product_variants(bom.product_tmpl_id)
                # update only if necessary
                if bom._update_bom(bom.std_cost_update_date):
                    product_variants.action_bom_cost()

        _logger.info("BOM Cost Rollup Process Completed")

        product_list = {}
        # FIXME: code smell - variable name reused
        bom_ids = self.sudo().search([("std_cost_update_date", ">=", current_time)])
        if bom_ids:
            _logger.info("BOM Cost Rollup Email Process Started")
            for bom in bom_ids:
                product_variants = self.get_product_variants(bom.product_tmpl_id)
                for variant in product_variants:
                    product_list[variant.default_code] = variant.standard_price

            # TODO: use an email template, no settings config will be needed then
            # Log if no user email to notify
            if not self.env.user.company_id.bom_cost_email:
                _logger.error(
                    "Exception while executing \
                    BoM Cost Rollup: \
                    Please configure email to notify from Company."
                )
            template_id = self.env.ref(
                "product_cost_rollup_to_bom.bom_cost_rollup_email_template"
            )
            template_id.with_context(
                {
                    "product_list_len": len(product_list),
                    "email_to": self.env.user.company_id.bom_cost_email,
                    "email_from": self.env.user.partner_id.email,
                    "product_list": product_list,
                }
            ).send_mail(self.id, force_send=True)

            _logger.info("BOM Cost Rollup Email Process Completed")
        else:
            _logger.info("No changes to BOM Cost Rollup. No Email.")
        return True
