1.  Go to *Manufacturing \> Products \> Bills of Materials* and set the
    *Manuf. Lead Time* of the BoM you want to plan from the
    finish date.
2.  Go to *Manufacturing \> Operations \> Manufacturing Orders* and
    create a new manufacturing order.
3.  Set the *Scheduled End* date to the desired finish date.
4.  The *Scheduled Date* (start) is automatically set to *Scheduled End*
    minus the BoM's *Manuf. Lead Time*, and the dates of the raw
    material moves are updated accordingly.

The company's *Security Lead Time* (*Manufacturing \> Configuration \>
Settings \> Planning*) is deliberately not taken into account here: it
is a replenishment setting, applied when a reordering rule schedules a
manufacturing order, and subtracting it as well would make the order
finish before the *Scheduled End* you asked for.
