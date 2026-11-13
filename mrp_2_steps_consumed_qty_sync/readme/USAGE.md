The module covers a production order whose components are picked and
consumed step by step, one work order after another, by different
operators:

1.  The warehouse manufactures in two steps (pick components, then
    produce), or in three steps.
2.  The bill of materials has several operations, for example *Weigh
    and cut* followed by other ones.
3.  Confirm the production order. A pick components picking is created
    with all the components.
4.  Start the first work order, so its time starts counting.
5.  Open the pick components picking and report the quantities actually
    taken from stock for this operation (for example by weighing them).
6.  Validate the picking creating a backorder with the components not
    used by this operation. The production order now holds exactly the
    picked quantities, and the components left in the backorder hold
    nothing.
7.  Start the next work order, open the backorder of the pick components
    picking, report what is used in this operation and validate it
    creating a new backorder with the remaining components. The
    production order is updated again with everything picked so far.
8.  Repeat the previous step until all the operations are finished.
    Validate the last pick components picking without backorder: the
    demand of the components that were never picked becomes zero in the
    production order and nothing is consumed for them, as they have not
    been used.
9.  Mark the production order as done. It consumes the picked
    quantities, with no need to report them again on the production
    order.

If less than planned is produced and the production order is closed
without backorder, it consumes everything picked.

If a backorder of the production order is created instead, the demand
is split in proportion to the quantity produced, as Odoo core does. The
production order consumes the part of the picked quantities proportional
to the quantity produced, never more than what has been picked, and the
rest stays reserved for the backorder, which consumes it when it is
done. The components still pending in the pick components backorder are
linked to the backorder of the production order and are consumed by it
when picked.

As the consumption is what has been picked, a bill of materials with the
*Warning* consumption shows the consumption warning when the picked
quantities differ from the expected ones for the quantity produced, also
before deciding whether a backorder is created.
