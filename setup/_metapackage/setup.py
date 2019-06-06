import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-mrp_auto_assign',
        'odoo10-addon-mrp_bom_comparison',
        'odoo10-addon-mrp_bom_component_find',
        'odoo10-addon-mrp_bom_component_menu',
        'odoo10-addon-mrp_bom_line_sequence',
        'odoo10-addon-mrp_bom_location',
        'odoo10-addon-mrp_bom_note',
        'odoo10-addon-mrp_mto_with_stock',
        'odoo10-addon-mrp_mto_with_stock_purchase',
        'odoo10-addon-mrp_no_partial',
        'odoo10-addon-mrp_production_note',
        'odoo10-addon-mrp_production_putaway_strategy',
        'odoo10-addon-mrp_production_request',
        'odoo10-addon-mrp_production_service',
        'odoo10-addon-mrp_progress_button',
        'odoo10-addon-mrp_repair_calendar_view',
        'odoo10-addon-mrp_repair_discount',
        'odoo10-addon-product_quick_bom',
        'odoo10-addon-quality_control',
        'odoo10-addon-quality_control_mrp',
        'odoo10-addon-quality_control_stock',
        'odoo10-addon-quality_control_team',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
