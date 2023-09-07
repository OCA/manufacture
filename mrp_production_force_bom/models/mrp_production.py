# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _force_bom(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_production_force_bom.force_bom")
        )
        if param == "1":
            return True
        return False

    def _skip_bom_check(self):
        """Extend this method as necessary to control whether or not to check the
        components against BoM.
        """
        self.ensure_one()
        return False

    def _check_component_discrepancies(self, error_messages):
        # Get all the components and their quantities using explode()
        factor = (
            self.product_uom_id._compute_quantity(
                self.product_qty, self.bom_id.product_uom_id
            )
            / self.bom_id.product_qty
        )
        _, lines_done = self.bom_id.explode(self.product_id, factor)
        expected_components = {}
        for line, data in lines_done:
            product_id = line.product_id.id
            expected_components[product_id] = (
                expected_components.get(product_id, 0) + data["qty"]
            )
        # Prepare a dictionary for the components and
        # their total quantities in the MO's raw materials
        mo_components = {}
        for move in self.move_raw_ids:
            product_id = move.product_id.id
            mo_components[product_id] = (
                mo_components.get(product_id, 0) + move.product_qty
            )
        # Check for any discrepancies
        for product_id, qty in expected_components.items():
            if product_id not in mo_components or mo_components[product_id] != qty:
                product_name = self.env["product.product"].browse(product_id).name
                error_messages.append(
                    "'%s': Discrepancy detected for product '%s'. Expected quantity: '%s',"
                    " Found quantity: '%s'."
                    % (self.name, product_name, qty, mo_components.get(product_id, 0))
                )
        # Check if there are extra products in move_raw_ids not present in the BOM
        for product_id in mo_components:
            if product_id not in expected_components:
                product_name = self.env["product.product"].browse(product_id).name
                error_messages.append(
                    "'%s': Product '%s' is not part of the BOM components."
                    % (self.name, product_name)
                )
        return error_messages

    def action_confirm(self):
        if not self._force_bom():
            return super(MrpProduction, self).action_confirm()
        error_messages = []
        for production in self:
            if production._skip_bom_check():
                continue
            if not production.bom_id:
                error_messages.append(
                    _("'%s': You cannot proceed without setting a BOM.")
                    % production.name
                )
                continue
            # Check for discrepancies
            error_messages = production._check_component_discrepancies(error_messages)
        if error_messages:
            raise ValidationError("\n".join(error_messages))
        return super(MrpProduction, self).action_confirm()
