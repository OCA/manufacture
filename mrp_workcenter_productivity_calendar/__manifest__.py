# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Workcenter Productivity Calendar",
    "summary": "Compute work order time tracking duration from the "
    "work center's resource calendar, deducting breaks such as lunch",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "development_status": "Beta",
    "maintainers": ["CristianoMafraJunior"],
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_workcenter_views.xml",
    ],
    "installable": True,
}
