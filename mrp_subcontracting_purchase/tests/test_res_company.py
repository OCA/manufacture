from odoo.tests import TransactionCase


class TestResCompany(TransactionCase):
    def setUp(self):
        super(TestResCompany, self).setUp()

    def test_create_per_company_rules(self):
        company = self.env.company
        result = company._create_per_company_rules()
        self.assertIsNone(result)
