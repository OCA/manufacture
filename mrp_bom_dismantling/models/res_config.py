# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MrpConfigSettings(models.TransientModel):
    """ Add settings for dismantling BOM.
    """
    _inherit = 'mrp.config.settings'

    dismantling_product_choice = fields.Selection([
        (0, "Main BOM product will be set randomly"),
        (1, "User have to choose which component to set as main BOM product")
    ], "Dismantling BOM")

    @api.multi
    def get_default_dismantling_product_choice(self, fields):
        product_choice = self.env["ir.config_parameter"].get_param(
            'mrp.bom.dismantling.product_choice', default=0
        )
        return {'dismantling_product_choice': product_choice}

    @api.multi
    def set_dismantling_product_choice(self):
        self.env["ir.config_parameter"].set_param(
            'mrp.bom.dismantling.product_choice',
            self.dismantling_product_choice
        )
