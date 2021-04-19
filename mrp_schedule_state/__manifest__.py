{
    "name": "MRP Schedule State",
    "version": "14.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "wizards/switch_schedule_state_view.xml",
        "views/mrp_production_view.xml",
        "views/mrp_workorder_view.xml",
        "security/ir.model.access.csv",
    ],
    "maintainer": "bealdav,florian-dacosta",
    "license": "AGPL-3",
    "installable": True,
}
