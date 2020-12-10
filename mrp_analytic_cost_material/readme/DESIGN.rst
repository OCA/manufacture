# Tech design

New module `mrp_analytic_cost_material`, "Track raw material costs as Analytic Items during the manufacturing process".
Depends on core `mrp` and `mrp_analytic` from https://github.com/OCA/account-analytic
Maturity: Alpha (this is a PoC, and only a piece for a larger puzzle)

## Migrate `mrp_analytic` to 14.0: 

As is a required dependency.
Reference: https://github.com/OCA/account-analytic/pull/275

## Analytic Item (`account.analytic.line`)

Add fields:
- "Related Stock Move" `stock_move_id` field, stores the related Stock Move, generated on stock reservation for an MO.
- "Related Manufacturing Order" `manufacturing_order_id` (`mrp.production`).
- "Project Category", related to `product_id.category_id`, stored.

Add Views:
- Search Filter: add filter "Related to MO"
- Search View add group by Manufacturing Order, group by Product Category
- Menu "Manufacturing > Reports > Analytic Items": opens existing Analytic Items views, with "Related to MO" filter enabled. 

## Stock Move

When stock is reserved for an MO, generate an Analytic Item for the materials cost, including:
- Analytic Account
- Related Stock Move
- Related MO
- Product
- Quantity
- Cost * -1 (should be a negative amount)

If the stock is unreserved, delete the corresponding Analytic Item.
