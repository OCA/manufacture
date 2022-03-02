import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mrp_bom_location>=15.0dev,<15.1dev',
        'odoo-addon-mrp_bom_tracking>=15.0dev,<15.1dev',
        'odoo-addon-mrp_multi_level>=15.0dev,<15.1dev',
        'odoo-addon-mrp_multi_level_estimate>=15.0dev,<15.1dev',
        'odoo-addon-mrp_planned_order_matrix>=15.0dev,<15.1dev',
        'odoo-addon-mrp_production_putaway_strategy>=15.0dev,<15.1dev',
        'odoo-addon-mrp_progress_button>=15.0dev,<15.1dev',
        'odoo-addon-mrp_warehouse_calendar>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
