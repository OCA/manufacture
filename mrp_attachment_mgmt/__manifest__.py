# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mrp Attachment Mgmt",
    "version": "14.0.1.1.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "installable": True,
    "data": [
        "views/mrp_bom_view.xml",
        "views/product_views.xml",
        "views/workorder_attachments_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
