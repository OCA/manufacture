To configure exception rules:

1.  Go to *Settings \> Technical \> Exception Rules*.
2.  Create a new rule.
3.  Select **Manufacturing Order** in the *Applies To* field.
4.  Define your rule using the provided options (e.g., By Domain, By
    Python Code).
5.  (Optional) Check the **Blocking** field if you want to strictly
    prevent this exception from being ignored by any user.

**Example rule (By Domain):** To block the completion of any
Manufacturing Order where the product quantity exceeds 1,000 units:

- **Exception Type:** By Domain
- **Domain:** `[('product_qty', '>', 1000)]`
