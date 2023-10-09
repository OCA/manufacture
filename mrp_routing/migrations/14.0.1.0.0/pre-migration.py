from openupgradelib.openupgrade import rename_xmlids


def migrate(cr, version):
    rename_xmlids(
        cr,
        [
            ("mrp.sequence_mrp_route", "mrp_routing.sequence_mrp_route"),
        ],
    )
