When you have several sales orders with make to order (MTO) products that
require to be manufactured, you end up with one manufacturing order for each of
these sales orders, which is very bad for the management.

With this module, each time an MTO manufacturing order is required to be
created, it first checks that there's no other existing order not yet started
for the same product and bill of materials inside the specied time frame , and
if there's one, then the quantity of that order is increased instead of
creating a new one.
