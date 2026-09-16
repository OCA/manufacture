This module integrates Manufacturing Orders with ``product_lot_sequence``.

It allows automatically generated lot and serial numbers in Manufacturing
Orders to use the sequence configured on the product when the lot sequence
policy is set to ``product``.

If no product-specific sequence is configured, the standard Odoo lot
generation behavior is used.
