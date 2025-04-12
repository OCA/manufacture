- An unbuild order not linked to a manufacturing order will not utilize
  the functionality of the stock_owner_restriction module.

- In case there are products with and without an owner assigned.
  Unbuilding a manufacturing order with an owner assigned will lead to
  a stock adjustment on the product without an assigned owner.
  While we actually expect that the product from the MO will be unbuild.
  (The one with the asisgned owner).

- The owner declared on the manufacturing order is assigned to the finished
  product without checking who owned the components that were actually
  consumed. An order carrying an owner that consumes the company's own stock
  (or stock belonging to another partner) still hands the output to that
  owner, so the consumed material leaves the company valuation with nothing
  recording it. Validating such an order is not blocked yet.
