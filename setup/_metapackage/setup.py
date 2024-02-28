import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_move_line_manufacture_info',
        'odoo13-addon-base_repair',
        'odoo13-addon-base_repair_config',
        'odoo13-addon-mrp_bom_component_menu',
        'odoo13-addon-mrp_bom_line_sequence',
        'odoo13-addon-mrp_bom_location',
        'odoo13-addon-mrp_bom_note',
        'odoo13-addon-mrp_bom_tracking',
        'odoo13-addon-mrp_multi_level',
        'odoo13-addon-mrp_multi_level_estimate',
        'odoo13-addon-mrp_planned_order_matrix',
        'odoo13-addon-mrp_production_grouped_by_product',
        'odoo13-addon-mrp_production_note',
        'odoo13-addon-mrp_production_putaway_strategy',
        'odoo13-addon-mrp_production_request',
        'odoo13-addon-mrp_sale_info',
        'odoo13-addon-mrp_stock_orderpoint_manual_procurement',
        'odoo13-addon-mrp_unbuild_tracked_raw_material',
        'odoo13-addon-mrp_warehouse_calendar',
        'odoo13-addon-mrp_workorder_sequence',
        'odoo13-addon-mrp_workorder_update_component',
        'odoo13-addon-product_cost_rollup_to_bom',
        'odoo13-addon-product_mrp_info',
        'odoo13-addon-product_quick_bom',
        'odoo13-addon-quality_control_mrp_oca',
        'odoo13-addon-quality_control_oca',
        'odoo13-addon-quality_control_stock_oca',
        'odoo13-addon-quality_control_team_oca',
        'odoo13-addon-repair_refurbish',
        'odoo13-addon-stock_picking_product_kit_helper',
        'odoo13-addon-stock_whole_kit_constraint',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
