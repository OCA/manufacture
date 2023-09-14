import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mrp_bom_component_menu>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_location>=16.0dev,<16.1dev',
        'odoo-addon-mrp_bom_tracking>=16.0dev,<16.1dev',
        'odoo-addon-mrp_multi_level>=16.0dev,<16.1dev',
        'odoo-addon-mrp_multi_level_estimate>=16.0dev,<16.1dev',
        'odoo-addon-mrp_production_note>=16.0dev,<16.1dev',
        'odoo-addon-mrp_production_quant_manual_assign>=16.0dev,<16.1dev',
        'odoo-addon-mrp_restrict_lot>=16.0dev,<16.1dev',
        'odoo-addon-mrp_sale_info>=16.0dev,<16.1dev',
        'odoo-addon-mrp_warehouse_calendar>=16.0dev,<16.1dev',
        'odoo-addon-quality_control_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
