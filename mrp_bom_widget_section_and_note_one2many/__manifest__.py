# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: BADEP
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Widget Section and Note in BoM",
    "summary": "Add section and note in Bills of Materials",
    "version": "17.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "author": "GRAP," "Odoo Community Association (OCA)",
    "maintainers": ["quentinDupont"],
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "account",
    ],
    "data": [
        "views/view_mrp_bom.xml",
    ],
    "installable": True,
}
