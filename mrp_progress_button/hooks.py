# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def fill_date_started(cr):
    """Create date_started and fill it from date_start for started orders, so
    the ORM does not compute it as the install/upgrade time."""
    cr.execute(
        """
        ALTER TABLE mrp_production
        ADD COLUMN IF NOT EXISTS date_started timestamp without time zone
        """
    )
    cr.execute(
        """
        UPDATE mrp_production
        SET date_started = date_start
        WHERE state IN ('progress', 'to_close', 'done')
            AND date_started IS NULL
        """
    )


def pre_init_hook(env):
    fill_date_started(env.cr)
