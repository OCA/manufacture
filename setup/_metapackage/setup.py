import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_repair',
        'odoo14-addon-mrp_account_analytic',
        'odoo14-addon-mrp_analytic_cost',
        'odoo14-addon-mrp_attachment_mgmt',
        'odoo14-addon-mrp_bom_location',
        'odoo14-addon-mrp_bom_tracking',
        'odoo14-addon-mrp_multi_level',
        'odoo14-addon-mrp_multi_level_estimate',
        'odoo14-addon-mrp_planned_order_matrix',
        'odoo14-addon-mrp_production_grouped_by_product',
        'odoo14-addon-mrp_production_putaway_strategy',
        'odoo14-addon-mrp_production_quant_manual_assign',
        'odoo14-addon-mrp_production_serial_matrix',
        'odoo14-addon-mrp_progress_button',
        'odoo14-addon-mrp_restrict_lot',
        'odoo14-addon-mrp_sale_info',
        'odoo14-addon-mrp_subcontracting_purchase_link',
        'odoo14-addon-mrp_warehouse_calendar',
        'odoo14-addon-mrp_workcenter_hierarchical',
        'odoo14-addon-mrp_workorder_sequence',
        'odoo14-addon-quality_control_oca',
        'odoo14-addon-quality_control_stock_oca',
        'odoo14-addon-repair_refurbish',
        'odoo14-addon-repair_stock_move',
        'odoo14-addon-repair_type',
        'odoo14-addon-stock_picking_product_kit_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
