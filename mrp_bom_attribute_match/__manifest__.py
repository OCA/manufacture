# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# Copyright 2026 CHEF PIXEL
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "BOM Attribute Match",
    "version": "19.0.1.0.0",
    "category": "Manufacturing",
    "author": "Ilyas, Ooops, CHEF PIXEL, Odoo Community Association (OCA)",
    "maintainer": "CHEF PIXEL",
    "summary": "Dynamic BOM component based on product attribute",
    "depends": ["mrp"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "support": "hello@chef-pixel.fr",
    "data": [
        "views/mrp_bom_views.xml",
    ],
    "installable": True,
}
