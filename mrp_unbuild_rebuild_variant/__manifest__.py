# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP unbuild rebuild variant",
    "summary": "Wrapper to easily unbuild a variant and rebuild another variant",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp", ],
    "data": [
        "data/ir.sequence.xml",
        "security/ir.model.access.csv",
        "views/mrp_unbuild_rebuild_variant.xml",
    ],
    "demo": ["demo/product.xml", ],
}
