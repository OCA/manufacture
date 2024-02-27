# Copyright (C) 2024-Today: GRAP (<http://www.grap.coop/>)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import SUPERUSER_ID, api


def initialize_product_variant_field(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for bom in env["mrp.bom"].search([]).filtered(lambda x: not x.product_id):
        bom.product_id = bom.product_tmpl_id.product_variant_ids[0]
