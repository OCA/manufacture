# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "MRP Stock Rule Propagate BOM Line",
    "summary": "Avoid grouping line of different kit in picking operations",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/stock_rule.xml",
    ],
}
