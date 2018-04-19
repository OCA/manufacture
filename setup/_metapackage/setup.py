import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-mrp_bom_note',
        'odoo8-addon-mrp_bom_reference_selection',
        'odoo8-addon-mrp_bom_version',
        'odoo8-addon-mrp_calendar_view',
        'odoo8-addon-mrp_disable_force_availability_button',
        'odoo8-addon-mrp_hook',
        'odoo8-addon-mrp_operations_extension',
        'odoo8-addon-mrp_operations_project',
        'odoo8-addon-mrp_operations_start_without_material',
        'odoo8-addon-mrp_operations_time_control',
        'odoo8-addon-mrp_produce_uos',
        'odoo8-addon-mrp_production_estimated_cost',
        'odoo8-addon-mrp_production_note',
        'odoo8-addon-mrp_production_partner_note',
        'odoo8-addon-mrp_production_raw_material_procurement_group',
        'odoo8-addon-mrp_production_real_cost',
        'odoo8-addon-mrp_project',
        'odoo8-addon-mrp_repair_discount',
        'odoo8-addon-mrp_sale_info',
        'odoo8-addon-procurement_mrp_no_confirm',
        'odoo8-addon-quality_control',
        'odoo8-addon-quality_control_force_valid',
        'odoo8-addon-quality_control_mrp',
        'odoo8-addon-quality_control_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
