# Copyright 2021 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Multiple Serial",
    "summary": "Manufacture multiple serialized products at once",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Le Filament, Odoo S.A., Odoo Community Association (OCA)",
    "maintainers": ["remi-filament"],
    "license": "GPL-3",
    "depends": [
        "mrp",
        "product_lot_sequence",
    ],
    "data": [
        # views
        "views/mrp_production.xml",
    ],
    "qweb": [
        # "static/src/xml/*.xml",
    ],
    "installable": True,
    "auto_install": False,
}
