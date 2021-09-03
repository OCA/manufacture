# Copyright 2021 Quartile Limited
# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Production - Manual Quant Assignment",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Quartile Limited, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp", "stock_quant_manual_assign"],
    "data": ["views/mrp_production_views.xml", "wizards/assign_manual_quants_view.xml"],
    "installable": True,
}
