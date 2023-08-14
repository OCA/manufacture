# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Input Configuration",
    "summary": "Allows encoding input data for products configuration",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mrp_bom_variable",
    ],
    "maintainer": [
        "bealdav",
    ],
    "data": [
        "views/input_config.xml",
        "views/input_line.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
