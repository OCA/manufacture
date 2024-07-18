# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # Overwrite the field domain for adding subcontracting BoMs with the check
    bom_id = fields.Many2one(
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        '|',
            ('type', '=', 'normal'),
            '&', ('type', '=', 'subcontract'), ('allow_in_regular_production', '=', True)
        ]""",
    )

    @api.model
    def create(self, values):
        """We must correctly set the workorder_ids field in subcontratactions.
        We allow to set workorders in mrp.bom if allow_in_regular_production is checked
        and it must be compatible.
        We do not want to use the _prepare_subcontract_mo_vals() method of stock.picking
        and set the workorder_ids there because mrp already has all the logic by UX in
        the _create_workorder() method, that is why it is done this way only for
        subcontractactions.
        """
        production = super().create(values)
        if self.env.context.get("force_subcontract_create_workorder"):
            warehouse = production.picking_type_id.warehouse_id
            if (
                production.picking_type_id == warehouse.subcontracting_type_id
                and production.bom_id.allow_in_regular_production
            ):
                production._onchange_workorder_ids()
        return production
