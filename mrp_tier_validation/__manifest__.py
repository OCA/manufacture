# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Tier Validation",
    "summary": "Extends the functionality of Productions to "
    "support a tier validation process.",
    "version": "18.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "TRESCLOUD, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "base_tier_validation"],
    "data": [
        "views/mrp_production_views.xml",
        "data/mrp_tier_validation_exception_data.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
