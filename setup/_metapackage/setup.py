import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-manufacture",
    description="Meta package for oca-manufacture Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-repair_refurbish',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
