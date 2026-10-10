# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Workorder Pause Note",
    "summary": """
        Adds a field to the MRP Workorder model to store
        the last note given by the operator when pausing that workorder.
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.1",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workorder_views.xml",
        "wizard/mrp_workorder_pause_note_wizard_views.xml",
    ],
}
