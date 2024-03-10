# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Mrp Bom Line Description",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "maintainers": ["dora-jurcevic"],
    "development_status": "Beta",
    "depends": [
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bom_line_description.xml",
        "views/mrp_bom_line.xml",
    ],
    "installable": True,
}
