This module can be used to customize the quantity of a component based
on a custom attribute value selected on the product. The following
configuration works when the website_sale module is installed.

In order to do that, configure as follows:

1.  Create an attribute "Component quantity" with a custom value

    ![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/product_attribute.png)

2.  Create and publish a Product having the configured custom value, and
    the MTO route (archived by default)

    ![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/product_tab_attributes.png)

3.  Add a BoM to the product, where one Component has the following
    formula for the quantity:

    ![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/bom.png)

    ``` python
    sale_lines = production.move_dest_ids.sale_line_id
    produced_template = production.product_tmpl_id
    produced_template_sale_line = sale_lines.filtered(lambda l: l.product_template_id == produced_template)
    custom_attributes_values = produced_template_sale_line.product_custom_attribute_value_ids.with_context(lang=None)
    component_quantity_attribute_value = custom_attributes_values.filtered(
        lambda av: av.custom_product_template_attribute_value_id.attribute_id.name == "Component quantity"
    )
    component_quantity = component_quantity_attribute_value.custom_value
    quantity = int(component_quantity)
    ```

4.  In the e-commerce, select a quantity for the custom value and buy
    the product

    ![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/website_sale_product.png)

5.  Confirm the sale order

    ![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/sale_order.png)

a Production order with the selected value of Component will be created

![image](https://raw.githubusercontent.com/OCA/manufacture/16.0/mrp_bom_line_formula_quantity/static/description/images/production_order.png)
