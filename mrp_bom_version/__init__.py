from . import models


def _post_install_set_active_bom_active_state(cr, registry):
    """Set those active BoMs to state 'active'"""
    cr.execute(
        """UPDATE mrp_bom
                     SET state = 'active'
                   WHERE active = True"""
    )
