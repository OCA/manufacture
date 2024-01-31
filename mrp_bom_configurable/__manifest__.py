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
        "views/input_config.xml",
        "views/input_line.xml",
        "views/input_constraint.xml",
        "views/bom.xml",
        "views/bom_line.xml",
        "views/input_line_wizard.xml",
        "views/sale_order.xml",
        "report/report.xml",
        "report/bom_configurable.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/mrp_bom_configurable.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_bom_configurable/static/src/**/*",
            ("remove", "mrp_bom_configurable/static/src/input_line_viewer/**/*"),
        ],
        "mrp_bom_configurable.input_line": [
            "mrp_bom_configurable/static/src/input_line_viewer/**/*"
        ],
    },
    "installable": True,
}
