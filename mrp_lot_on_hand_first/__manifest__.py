# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Mrp Lot On Hand First",
    "summary": "Allows to display lots on hand first in M2o fields",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "mrp",
        "stock_lot_on_hand_first",
    ],
    "data": [
        "views/mrp_production.xml",
        "views/stock_picking_type.xml",
    ],
}
