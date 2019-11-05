import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_move_line_manufacture_info',
        'odoo12-addon-mrp_auto_assign',
        'odoo12-addon-mrp_bom_component_menu',
        'odoo12-addon-mrp_bom_line_sequence',
        'odoo12-addon-mrp_bom_location',
        'odoo12-addon-mrp_bom_tracking',
        'odoo12-addon-mrp_multi_level',
        'odoo12-addon-mrp_multi_level_estimate',
        'odoo12-addon-mrp_production_auto_post_inventory',
        'odoo12-addon-mrp_production_grouped_by_product',
        'odoo12-addon-mrp_production_putaway_strategy',
        'odoo12-addon-mrp_production_request',
        'odoo12-addon-mrp_stock_orderpoint_manual_procurement',
        'odoo12-addon-mrp_unbuild_tracked_raw_material',
        'odoo12-addon-mrp_warehouse_calendar',
        'odoo12-addon-mrp_workorder_sequence',
        'odoo12-addon-product_mrp_info',
        'odoo12-addon-quality_control',
        'odoo12-addon-quality_control_issue',
        'odoo12-addon-quality_control_stock',
        'odoo12-addon-quality_control_team',
        'odoo12-addon-repair_refurbish',
        'odoo12-addon-stock_picking_product_kit_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
