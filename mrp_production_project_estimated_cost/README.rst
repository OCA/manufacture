Estimated costs in manufacturing orders
=======================================
With this module when a production order is confirmed, some analytic lines
are automatically generated, in order to estimate the costs of the production
order.

At the same time, the estimated allocation of materials, machinery operators
and costs will be made.

In materials case, an analytic line will be generated for each material to
consume in the order. For operators imputation in each operation, it will
be generated one line, so that the number of lines will be equal to the number
of operators in the operation. In machines case, there will be created two
analytic lines for each operation in the associated routing, one per hour cost
and the other per cycle cost.

It has also created the new menu option "Fictitious Manufacturing Orders to
estimate costs". When a new MO is created and the new field "active" is equal
to false, the MO will be considered as a fictional MO, what with can not be
confirmed, and only is valid to estimate costs. To estimate costs will have to
press the "Compute data" button in tab "Work Orders". These fictitious MO will
have a different sequence.
From the product form may create a fictitious MO.

