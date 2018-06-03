To configure the time frame for grouping manufacturing order:

#. Go to *Inventory > Configuration > Warehouse Management > Operation Types*
#. Locate the manufacturing type you are using (default one is called
   "Manufacturing").
#. Open it and change these 2 values:

   * MO grouping max. hour (UTC): The maximum hour (between 0 and 23) for
     considering new manufacturing orders inside the same interval period, and
     thus being grouped on the same MO. IMPORTANT: The hour should be expressed
     in UTC.
   * MO grouping interval (days): The number of days for grouping together on
     the same manufacturing order.

   Example: If you leave the default values 19 and 1, all the planned orders
   between 19:00:01 of the previous day and 20:00:00 of the target date will
   be grouped together.
