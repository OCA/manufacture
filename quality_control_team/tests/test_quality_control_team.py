# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestQualityControlTeam(TransactionCase):

    def setUp(self):
        super(TestQualityControlTeam, self).setUp()
        self.qc_team_obj = self.env['qc.team']
        self.main_qc_team = self.env.ref('quality_control_team.qc_team_main')
        self.other_company = self.env['res.company'].create({
            'name': 'other company',
        })
        self.user_test = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'company_id': self.other_company.id,
            'company_ids': [(4, self.other_company.id)],
        })

    def test_default_qc_team(self):
        """Test that the QC team is defaulted correctly."""
        team = self.qc_team_obj._get_default_qc_team_id(
            user_id=self.user_test.id)
        self.assertEqual(team, self.main_qc_team)
        test_team = self.qc_team_obj.create({
            'name': 'Test Team',
            'user_id': self.user_test.id,
            'company_id': self.other_company.id,
        })
        team = self.qc_team_obj._get_default_qc_team_id(
            user_id=self.user_test.id)
        self.assertEqual(team, test_team)
