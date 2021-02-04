# 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Load",
    "version": "14.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "summary": "Workcenters load computing",
    "category": "Manufacturing",
    "depends": [
        "mrp_workcenter_hierarchical",
        # 'mrp_workcenter_workorder_link',
    ],
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "views/workcenter_view.xml",
        "wizards/substitute_workcenter.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["data/mrp_demo.xml"],
    "license": "AGPL-3",
    "installable": True,
}
