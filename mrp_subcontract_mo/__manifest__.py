# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Subcontract Manufacturing Order",
    "summary": "Manufacturing Order Subcontracting Choice",
    "version": "12.0.1.0.0",
    "development_status": "Production",
    "category": 'Manufacturing',
    "website": "https://github.com/OCA/manufacture",
    "author": "Scopea, Le Filament, Odoo Community Association (OCA)",
    "maintainers": ["remi-filament", ],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'purchase_mrp',
    ],
    "data": [
        'data/location.xml',
        'data/picking_type.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/mrp_production_view.xml',
        'wizard/mrp_subcontract_view.xml',
    ],
    "demo": [
        "demo/demo_res_partner.xml",
        "demo/demo_product.xml",
        "demo/demo_mrp_workcenter.xml",
        "demo/demo_mrp_routing.xml",
        "demo/demo_mrp_bom.xml",
    ],
}
