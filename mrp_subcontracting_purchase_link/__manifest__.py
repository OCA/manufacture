# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Link Purchase Order Line to Subcontract Productions",
    "version": "14.0.2.0.0",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["purchase", "mrp_subcontracting"],
    "data": ["views/purchase_order_views.xml", "views/mrp_production_views.xml"],
    "installable": True,
}
