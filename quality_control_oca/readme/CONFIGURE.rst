* Question: The thing to be checked. We have two types of questions:

* Qualitative: The result is a description, color, yes, no...

* Quantitative: The result must be within a range.

* Possible values: The values chosen in qualitative questions.

* Test: The set of questions to be used in inspections.

* Once these values are set, we define the inspection.

We have a *generic* test that can be applied to any model: shipments,
invoices or product, or a *test related*, making it specific to a particular
product and that eg apply whenever food is sold or when creating a batch.

Once these parameters are set, we can just pass the test. We create a
new inspection, selecting a relationship with the model (sale, stock move...),
and pressing "Select test" button to choose the test to pass. Then, you must
fill the lines depending on the chosen test.

The complete inspection workflow is:

    Draft -> Confirmed -> Success
                |
                | -> Failure (Pending approval) -> Approved
