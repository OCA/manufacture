# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Produce Delay in Hour",
    "summary": "Glue module for mrp_bom_produce_delay and mrp_product_produce_delay_in_hour",
    "version": "16.0.1.0.0",
    "author": "GRAP, Odoo Community Association (OCA)",
    "category": "Manufacturing",
    "depends": [
        "mrp_bom_produce_delay",
        "mrp_product_produce_delay_in_hour",
    ],
    "maintainers": ["quentinDupont"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "data": [
        "views/mrp_bom.xml",
    ],
    "installable": True,
    "auto_install": True,
}
