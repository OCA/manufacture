# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "MRP Production Check BoM Alignment",
    "summary": (
        "Verify that a Manufacturing Order's components "
        "and workorder are consistent with its Bill of "
        "Materials."
    ),
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "18.0.1.0.4",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mrp_bom_alignment_warning_views.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
