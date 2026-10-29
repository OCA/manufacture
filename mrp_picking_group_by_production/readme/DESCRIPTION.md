In multi-step manufacturing, the components that the *Pick Components*
transfer takes from stock and the finished products that the *Store Finished
Product* transfer puts away are grouped into a single transfer whenever the
manufacturing orders share a reference, for example several orders created
from the same sale order or from a chain of replenishments. Odoo only keeps
one transfer per manufacturing order when the component moves are chained to
the order, which is not the case with the *Take From Stock, if unavailable,
Trigger Another Rule* supply method used by the standard pick components rule.

This module creates one transfer per manufacturing order for those moves, so
the warehouse always knows which order a pick components or store finished
product transfer belongs to.
