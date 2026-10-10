{
    "name": "MRP Work Center Safety Symbols",
    "version": "18.0.1.0.0",
    "summary": """
        This module allows associating predefined ISO 7010 safety symbols
        (from the 'base_iso7010' module) with Manufacturing Work Centers.

        It provides the technical link and the user interface modification
        on the Work Center form.

        To load actual symbols, install 'base_iso7010' and relevant
        'base_iso7010_data_*' modules.
    """,
    "author": "bosd, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "depends": [
        "mrp",
        "base_iso7010",
    ],
    "data": [
        "views/mrp_workcenter_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
