# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Automatic creation of the MTO+MTS rule when creating a Subcontractor.",
    "version": "14.0.1.0.1",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_subcontracting_partner_management", "stock_mts_mto_rule"],
    "data": [
        "views/res_partner.xml",
        # "views/mrp_production_views.xml"
    ],
    "installable": True,
}
