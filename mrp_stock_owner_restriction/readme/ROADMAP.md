- An unbuild order not linked to a manufacturing order will not utilize
  the functionality of the stock_owner_restriction module.

- In case there are products with and without an owner assigned.
  Unbuilding a manufacturing order with an owner assigned will lead to
  a stock adjustment on the product without an assigned owner.
  While we actually expect that the product from the MO will be unbuild.
  (The one with the asisgned owner).
