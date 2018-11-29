# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP Production Request",
    "summary": "Allows you to use Manufacturing Request as a previous "
               "step to Manufacturing Orders for better manufacture "
               "planification.",
    "version": "11.0.1.0.0",
    "development_status": "Mature",
    "maintainers": ['lreficent'],
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp", "stock_available_unreserved"],
    "data": [
        "security/mrp_production_request_security.xml",
        "security/ir.model.access.csv",
        "data/mrp_production_request_sequence.xml",
        "wizards/mrp_production_request_create_mo_view.xml",
        "views/mrp_production_request_view.xml",
        "views/product_template_view.xml",
        "views/mrp_production_view.xml",
    ],
}
