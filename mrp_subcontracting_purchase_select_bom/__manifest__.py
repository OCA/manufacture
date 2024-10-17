# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Subcontracting Purchase Select BoM",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "summary": "Select bill of material on purchase order line",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "development_status": "Mature",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_subcontracting_purchase"],
    "data": [
        "views/purchase_order.xml",
        "views/purchase_order_line.xml",
        "views/mrp_bom.xml",
    ],
    "installable": True,
}
