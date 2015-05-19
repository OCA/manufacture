Estimated costs in manufacturing orders
=======================================

Thanks to this module, when a Manufacturing Order is confirmed, analytic lines
are automatically generated in order to estimate the costs of the production
order.

At the same time, the estimated allocation of raw materials, machine operators
time and costs will be made as followed:

* Raw Material cost: an analytic line will be generated for each material to
  be consumed in the order.
* Operators time: One line will be generated for the time recorded by the
  operators in each operation, so that the number of lines will be equal to
  the number of operators in the operation.
* Cost associated to machines: two analytic lines for each operation will be
  created in the associated routing, one for hourly cost and the other for per
  cycle cost.

A new menu is available "Virtual Manufacturing Orders for cost estimation"
where the user can managed virtual MO:

* When a new MO is created and the new field "active" is false, the MO will be
  considered virtual. It is only used for cost estimation and can not be
  confirmed.
* To estimate the cost of the MO, the user has to press the button "Compute
  data" in the tab "Work Orders".
* These virtual MO have a separate sequence number.
* The user can create a virtual MO directly from the product form.
