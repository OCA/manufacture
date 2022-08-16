# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


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
