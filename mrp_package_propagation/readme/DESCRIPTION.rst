Allow to propagate a package from a component to a finished product.

This is useful for instance if you want to keep the box of one of the component
(which could have already a label stuck on it) for your finished product.

Two constraints:

* the component quantity has to be 1 unit
* the manufacturing order has to produce exactly the BoM quantity

This is to ensure we get only one package reserved for the given component.
