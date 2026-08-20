To use this module, you need to:

1. Configure the ``product_lot_sequence.policy`` system parameter as ``product``.
2. Configure a lot sequence on a product tracked by lots or serial numbers.
3. Create a Manufacturing Order for the product.
4. Generate the lot or serial number automatically from the Manufacturing Order.
5. Verify that the generated lot or serial number uses the sequence configured on the product.

If the product does not have a specific lot sequence configured, the standard
Odoo lot generation behavior will be used.

When the lot sequence policy is set to ``global``, the standard Odoo lot
generation behavior is preserved.
