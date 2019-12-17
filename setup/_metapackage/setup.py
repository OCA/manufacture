import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-mrp_bom_component_menu',
        'odoo13-addon-mrp_warehouse_calendar',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
