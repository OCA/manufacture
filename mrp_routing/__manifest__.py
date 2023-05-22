# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Routing",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "maintainers": ["ChrisOForgeFlow"],
    "development_status": "Alpha",
    "depends": [
        "mrp",
    ],
    "data": [
        "data/sequence_data.xml",
        "security/ir.model.access.csv",
        "views/mrp_bom_view.xml",
        "views/mrp_routing_view.xml",
        "views/mrp_routing_workcenter_view.xml",
        "views/mrp_routing_workcenter_template_view.xml",
    ],
    "demo": [
        "demo/routing_data.xml",
    ],
    "installable": True,
}
