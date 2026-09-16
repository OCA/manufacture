{
    "name": "Manufacturing Exceptions",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Add custom exception rules to Manufacturing Orders",
    "author": "Global Protection, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "base_exception",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_exception_confirm_views.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
