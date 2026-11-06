In a Make To Order flow, the finished move of a manufacturing order feeds
the ensuing moves (e.g. the delivery). By default, if the manufacturing
order produces a different quantity than the planned one, the demand of
these ensuing moves is not updated.

This module pushes the change of quantity produced to the demand of the
ensuing moves, along the whole chain of destination moves:

- Producing more than planned increases the demand.
- Producing less than planned without creating a backorder decreases the
  demand.
- Producing less than planned and creating a backorder for the remaining
  quantity keeps the demand unchanged, as the backorder will still produce it.
- Cancelling a backorder manufacturing order decreases the demand by its
  remaining quantity.

Moves whose demand is reduced to zero are cancelled. Component moves of
another manufacturing order are never updated.
