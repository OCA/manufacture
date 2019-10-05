import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-mrp_bom_component_menu',
        'odoo9-addon-mrp_bom_dismantling',
        'odoo9-addon-mrp_bom_location',
        'odoo9-addon-mrp_bom_note',
        'odoo9-addon-mrp_bom_product_details',
        'odoo9-addon-mrp_disable_force_availability_button',
        'odoo9-addon-mrp_mto_with_stock',
        'odoo9-addon-mrp_production_note',
        'odoo9-addon-mrp_production_partner_note',
        'odoo9-addon-mrp_production_putaway_strategy',
        'odoo9-addon-mrp_production_raw_material_procurement_group',
        'odoo9-addon-mrp_production_request',
        'odoo9-addon-mrp_production_unreserve',
        'odoo9-addon-mrp_repair_refurbish',
        'odoo9-addon-mrp_sale_info',
        'odoo9-addon-quality_control',
        'odoo9-addon-quality_control_issue',
        'odoo9-addon-quality_control_team',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
