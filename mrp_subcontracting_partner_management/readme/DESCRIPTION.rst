The goal of this module is to make a partner ready for subcontracting flow (as per mrp_subcontracting_purchase features) and simplify their subcontracting management.

It adds a new checkbox "Subcontractor" in partner, which when enabled creates the following entities:

* A child location in the "Subcontracting" location
* A new 'Buy' stock rule for "Dropship Subcontractor on Order" route
* A new 'Pull from' stock rule for "Dropship Subcontractor on Order" route
