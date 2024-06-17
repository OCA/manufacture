import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_move_line_mrp_info>=16.0dev,<16.1dev',
        'odoo-addon-mrp_attachment_mgmt>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_component_menu>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_hierarchy>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_line_formula_quantity>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_location>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_tracking>=16.0dev,<16.1dev',
        'odoo-addon-mrp_default_workorder_time>=16.0dev,<16.1dev',
        'odoo-addon-mrp_lot_number_propagation>=16.0dev,<16.1dev',
        'odoo-addon-mrp_lot_production_date>=16.0dev,<16.1dev',
        'odoo-addon-mrp_multi_level>=16.0dev,<16.1dev',
        'odoo-addon-mrp_multi_level_estimate>=16.0dev,<16.1dev',
        'odoo-addon-mrp_packaging_default>=16.0dev,<16.1dev',
        'odoo-addon-mrp_planned_order_matrix>=16.0dev,<16.1dev',
        'odoo-addon-mrp_production_note>=16.0dev,<16.1dev',
        'odoo-addon-mrp_production_quant_manual_assign>=16.0dev,<16.1dev',
        'odoo-addon-mrp_restrict_lot>=16.0dev,<16.1dev',
        'odoo-addon-mrp_sale_info>=16.0dev,<16.1dev',
        'odoo-addon-mrp_subcontracting_bom_dual_use>=16.0dev,<16.1dev',
        'odoo-addon-mrp_subcontracting_inhibit>=16.0dev,<16.1dev',
        'odoo-addon-mrp_subcontracting_partner_management>=16.0dev,<16.1dev',
        'odoo-addon-mrp_subcontracting_purchase_link>=16.0dev,<16.1dev',
        'odoo-addon-mrp_subcontracting_skip_no_negative>=16.0dev,<16.1dev',
        'odoo-addon-mrp_tag>=16.0dev,<16.1dev',
        'odoo-addon-mrp_unbuild_move_link>=16.0dev,<16.1dev',
        'odoo-addon-mrp_unbuild_valuation_layer_link>=16.0dev,<16.1dev',
        'odoo-addon-mrp_warehouse_calendar>=16.0dev,<16.1dev',
        'odoo-addon-mrp_workcenter_cost>=16.0dev,<16.1dev',
        'odoo-addon-mrp_workcenter_hierarchical>=16.0dev,<16.1dev',
        'odoo-addon-mrp_workorder_lot_display>=16.0dev,<16.1dev',
        'odoo-addon-mrp_workorder_sequence>=16.0dev,<16.1dev',
        'odoo-addon-quality_control_oca>=16.0dev,<16.1dev',
        'odoo-addon-quality_control_stock_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
