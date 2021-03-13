To use this module, you need to:

#. Go to *Manufacturing > Manufacturing Requests*.
#. Create a manufacturing request or open a existing one (assigned to you or
   created from a procurement).
#. If you click on *Request approval* button the user assigned as approver
   will be added to the thread.
#. If you are the approver you can either click on *Approve* or *Reject*
   buttons.
#. Rejecting a MR will cancel it and propagate this cancellation to
   destination moves.
#. Approving a MR will allow you to create manufacturing orders.
#. You can manually set to done a request by clicking in the button *Done*.

To create MOs from MRs you have to:

#. Go to approved manufacturing request.
#. Click on the button *Create Manufacturing Order*.
#. In the opened wizard, click on *Compute lines* so you will have a
   quantity proposed for creating a MO. This quantity is the maximum quantity
   you can produce with the current stock available for the components needed
   in the source location.
#. Use the proposed quantity or change it and click on *Create MO* at the
   bottom of the wizard.

**NOTE:** This module does not restrict the quantity that can be converted
from a MR to MOs. It is in hands of the user to decide when a MR is ended and
to set it to *Done* state.
