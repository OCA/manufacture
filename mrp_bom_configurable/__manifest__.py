# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Bom Configurable",
    "summary": "Skip components lines in bom according to conditions",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "sale", "web"],
    "maintainer": [
        "bealdav",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/bom.xml",
        "views/bom_line.xml",
        "views/input_config.xml",
        "views/input_constraint.xml",
        "views/input_line.xml",
        "views/input_line_wizard.xml",
    ],
    "demo": [
        "demo/mrp_bom_configurable.xml",
    ],
    "installable": True,
}
