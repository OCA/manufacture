import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_move_line_manufacture_info',
        'odoo13-addon-mrp_bom_component_menu',
        'odoo13-addon-mrp_bom_line_sequence',
        'odoo13-addon-mrp_bom_location',
        'odoo13-addon-mrp_bom_tracking',
        'odoo13-addon-mrp_multi_level',
        'odoo13-addon-mrp_multi_level_estimate',
        'odoo13-addon-mrp_planned_order_matrix',
        'odoo13-addon-mrp_production_grouped_by_product',
        'odoo13-addon-mrp_production_putaway_strategy',
        'odoo13-addon-mrp_production_request',
        'odoo13-addon-mrp_warehouse_calendar',
        'odoo13-addon-mrp_workorder_sequence',
        'odoo13-addon-repair_calendar_view',
        'odoo13-addon-repair_refurbish',
        'odoo13-addon-stock_picking_product_kit_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
