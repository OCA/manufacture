# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Project Link",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Link production with projects",
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Antiun Ingeniería S.L.,"
              "Rotafilo - José Luis Sandoval Alaguna,"
              "Odoo Community Association (OCA)",
    "description": """
MRP Project Link
================
Link production with projects
        """,
    "maintainers": ['sergiocorato'],
    "depends": [
        "mrp_analytic",
        "sale_mrp_link",
        "project",
        "hr_timesheet",
    ],
    "data": [
        "wizard/mrp_production_createproject_views.xml",
        "views/account_analytic_line_view.xml",
        "views/hr_timesheet_views.xml",
        "views/mrp_production_views.xml",
        "views/project_view.xml",
        "views/project_task_view.xml"
    ],
    "installable": True,
}
