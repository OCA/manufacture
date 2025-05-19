# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Mass Production Order",
    "summary": "Create multiple manufacturing orders in one step",
    "version": "17.0.2.2.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Antoni Marroig, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_tag",
    ],
    "data": ["wizards/mrp_mass_order_wizard.xml", "security/ir.model.access.csv"],
}
