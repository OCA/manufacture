In the context of real time inventory valuation, this module will allow you to
automatically reconcile the interim accounts used in manufacturing and unbuild orders.

Typically a manufacturing order will produce the following journal entries:

Components:

* Dr. Manufacturing WIP
* Cr. Inventory


Finished product

* Dr. Inventory
* Cr. Manufacturing WIP

You would define the account 'Manufacturing WIP' in the *Virtual Locations/Production* location.

Once the manufacturing order has been completed the debits and credits in the 'Manufacturing WIP'
account should be balanced, and with this module, they will be reconciled.
