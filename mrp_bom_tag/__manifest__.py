# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Tag",
    "summary": "Add tags on your BoM to find it easily",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "author": "GRAP, , Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "demo": ["demo/mrp_bom_tag.xml"],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/view_mrp_bom.xml",
        "views/view_mrp_bom_tag.xml",
    ],
    "installable": True,
}
