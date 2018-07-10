import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-mrp_auto_assign',
        'odoo11-addon-mrp_bom_equivalent',
        'odoo11-addon-mrp_bom_location',
        'odoo11-addon-mrp_mto_with_stock',
        'odoo11-addon-mrp_production_grouped_by_product',
        'odoo11-addon-mrp_production_service',
        'odoo11-addon-mrp_warehouse_calendar',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
