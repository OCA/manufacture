To see this module effect :
- Unarchive `Replenish on Order (MTO)` in Inventory > Configuration > Routes
- Create a new Product with no stock
- Set Routes for this new Product : go to `Inventory` notebook and tick `Replenish on Order (MTO)` and `Manufacture`
- Create a Sale with this product
- It will trigger a new Manufacturing Order

.. figure:: ../static/description/bom_purchase_printing_wizard.png

.. figure:: ../static/description/sale_order_production_order_link.jpeg
