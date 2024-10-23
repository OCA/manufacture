# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Workcenter Workorder Link",
    "version": "16.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "summary": "Switch easily between Work Centers and Work Orders",
    "maintainers": ["florian-dacosta"],
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "views/mrp_workcenter_views.xml",
        "views/mrp_workorder_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
