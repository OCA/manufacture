import logging

from psycopg2 import sql


def pre_init_hook(cr):
    """Precreate move_type and fill with appropriate values to prevent
    a MemoryError when the ORM attempts to call its compute method on a large
    amount of preexisting moves. Note that the order of the mapping is
    important as one move can have move lines on accounts of multiple types
    and the move type is set in the order of precedence."""
    logger = logging.getLogger(__name__)
    logger.info("Add mrp_info")
    cr.execute(
        "ALTER TABLE account_move_line ADD COLUMN IF NOT EXISTS mrp_production_id INTEGER"
    )
    query = sql.SQL(
        """
        with q2 as (
        select aml.id as account_move_id,
        coalesce(sm.production_id,sm.raw_material_production_id) as mrp_id
        from account_move_line aml
        inner join stock_move sm
        on sm.id=aml.stock_move_id
        where coalesce(sm.production_id,sm.raw_material_production_id) is not null)
        update account_move_line
        set mrp_production_id = q2.mrp_id
        from q2
        where q2.account_move_id=account_move_line.id;
        """
    )
    cr.execute(query)
    cr.execute(
        "ALTER TABLE account_move_line ADD COLUMN IF NOT EXISTS unbuild_id INTEGER"
    )
    query = sql.SQL(
        """
        with q2 as (
        select aml.id as account_move_id,
        sm.unbuild_id as unb_id
        from account_move_line aml
        inner join stock_move sm
        on sm.id=aml.stock_move_id
        where sm.unbuild_id is not null)
        update account_move_line
        set unbuild_id = q2.unb_id
        from q2
        where q2.account_move_id=account_move_line.id;
        """
    )
    cr.execute(query)
