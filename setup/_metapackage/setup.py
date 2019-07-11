import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-mrp_auto_assign',
        'odoo12-addon-mrp_bom_component_menu',
        'odoo12-addon-mrp_bom_location',
        'odoo12-addon-mrp_bom_tracking',
        'odoo12-addon-mrp_production_grouped_by_product',
        'odoo12-addon-mrp_production_putaway_strategy',
        'odoo12-addon-mrp_warehouse_calendar',
        'odoo12-addon-quality_control',
        'odoo12-addon-repair_refurbish',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
