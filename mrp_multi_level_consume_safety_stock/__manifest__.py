# Copyright 2023 Camptocamp  (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Multi Level Consume Safety Stock",
    "version": "15.0.1.10.4",
    "development_status": "Production/Stable",
    "license": "LGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["gurneyalex"],
    "summary": "MRP scheduler: use safety stock during stress periods",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp_multi_level"],
    "data": ["views/mrp_area_views.xml"],
    "installable": True,
    "application": True,
}
