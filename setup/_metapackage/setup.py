import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mrp_account_bom_attribute_match>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_attribute_match>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_component_menu>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_hierarchy>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_location>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_tracking>=15.0dev,<15.1dev',
        'odoo-addon-mrp_finished_backorder_product>=15.0dev,<15.1dev',
        'odoo-addon-mrp_lot_number_propagation>=15.0dev,<15.1dev',
        'odoo-addon-mrp_lot_on_hand_first>=15.0dev,<15.1dev',
        'odoo-addon-mrp_multi_level>=15.0dev,<15.1dev',
        'odoo-addon-mrp_multi_level_estimate>=15.0dev,<15.1dev',
        'odoo-addon-mrp_planned_order_matrix>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_component_availability_search>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_date_planned_finished>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_grouped_by_product>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_putaway_strategy>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_serial_matrix>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_split>=15.0dev,<15.1dev',
        'odoo-addon-mrp_progress_button>=15.0dev,<15.1dev',
        'odoo-addon-mrp_sale_info>=15.0dev,<15.1dev',
        'odoo-addon-mrp_subcontracting_no_negative>=15.0dev,<15.1dev',
        'odoo-addon-mrp_tag>=15.0dev,<15.1dev',
        'odoo-addon-mrp_warehouse_calendar>=15.0dev,<15.1dev',
        'odoo-addon-mrp_workorder_sequence>=15.0dev,<15.1dev',
        'odoo-addon-quality_control_oca>=15.0dev,<15.1dev',
        'odoo-addon-stock_whole_kit_constraint>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
