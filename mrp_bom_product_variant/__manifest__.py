# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP BoM Product Variant",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "GRAP, Odoo Community Association (OCA)",
    "summary": "Makes Product variant required to create a Bill of Material",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/view_mrp_bom.xml",
    ],
    "installable": True,
    "post_init_hook": "initialize_product_variant_field",
}
