{
    "name": "MRP Work Center Safety Symbols Specification",
    "version": "18.0.1.0.0",
    "summary": """
         This module enhances the link between Work Centers and Safety Symbols
         (provided by 'mrp_workcenter_safety_symbol') by allowing users to add
         specific textual instructions or specifications for each linked symbol.

         It replaces the simple symbol selection widget with an editable list view
         on the Work Center form.
     """,
    "author": "bosd, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "depends": [
        "mrp_workcenter_safety_symbol",
    ],
    # Specify data files
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workcenter_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
