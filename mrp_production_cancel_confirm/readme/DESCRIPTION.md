When the user clicks on the Cancel button of a manufacturing order, a
confirmation wizard is shown, where a cancellation reason can optionally
be given. The reason, the user and the date are then stored on the
manufacturing order.

It replaces the plain confirmation dialog of the standard Cancel button,
and it also covers the Cancel button of the list view, which has no
confirmation at all in the standard behaviour.

The wizard is only shown when the cancellation is requested from the
Cancel button of the form or list views. Manufacturing orders cancelled
by other flows, such as deleting the order or cancelling a subcontracted
receipt, are not affected.
