If a product has a bill of materials (BoM) of subcontracting type, and
the vendor is included in the list of subcontractors of such BoM, when
doing a purchase order for such vendor and product, it will always
generate a subcontracting order. This module allows to inhibit such
behavior, acting as a regular purchase, as this may not be convenient in
some cases, as on manufacturing world, it's frequent that your vendor
sells you directly the same product without you providing any raw
material depending on lead times, material availability, etc. A check is
provided at purchase order line level for easily disable the
subcontracting part, as well as the same check at stock rule for
propagating the preference from replenishment option.
