# Copyright 2019 Kitti U. - Ecosoft <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Product Kit Helper",
    "summary": "Set quanity in picking line based on product kit quantity",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/manufacture",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_mrp"],
    "data": ["security/ir.model.access.csv", "views/stock_view.xml"],
    "maintainers": ["kittiu"],
}
