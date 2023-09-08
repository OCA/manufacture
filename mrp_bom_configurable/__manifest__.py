# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Bom Configurable",
    "summary": "Skip components lines in bom according to conditions",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "sale",
    ],
    "maintainer": [
        "bealdav",
    ],
    "data": [
        "views/input_config.xml",
        "views/input_line.xml",
        "views/mrp_view.xml",
        "report/report.xml",
        "report/bom_configurable.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/mrp_bom_configurable.xml",
    ],
    "assets": {"web.assets_backend": ["mrp_bom_configurable/static/src/**/*"]},
    "installable": True,
}
