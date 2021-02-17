import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-mrp_analytic_cost_material',
        'odoo14-addon-mrp_bom_location',
        'odoo14-addon-mrp_warehouse_calendar',
        'odoo14-addon-mrp_workcenter_hierarchical',
        'odoo14-addon-repair_refurbish',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
