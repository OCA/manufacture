import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_move_line_manufacture_info',
        'odoo13-addon-mrp_bom_component_menu',
        'odoo13-addon-mrp_bom_location',
        'odoo13-addon-mrp_bom_tracking',
        'odoo13-addon-mrp_multi_level',
        'odoo13-addon-mrp_production_grouped_by_product',
        'odoo13-addon-mrp_warehouse_calendar',
        'odoo13-addon-stock_picking_product_kit_helper',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
