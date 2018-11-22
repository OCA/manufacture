# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common
from odoo.exceptions import AccessError


class TestQualityControlIssue(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestQualityControlIssue, cls).setUpClass()

        cls.qc_problem_grp_obj = cls.env['qc.problem.group']
        cls.qc_problem_obj = cls.env['qc.problem']
        cls.qc_stage_obj = cls.env['qc.stage']
        cls.qc_issue_obj = cls.env['qc.issue']
        cls.qc_issue_stage_obj = cls.env['qc.issue.stage']
        cls.qc_team_obj = cls.env['qc.team']
        cls.stock_scrap_obj = cls.env['stock.scrap']
        cls.product = cls.env['product.product']
        cls.partner = cls.env['res.partner']
        cls.res_users = cls.env['res.users']
        cls.company = cls.env.ref('base.main_company')

        # Create Users and Groups
        # User assigned to quality control user group
        cls.group_qc_user = cls.env.ref(
            'quality_control.group_quality_control_user')
        cls.group_user = cls.env.ref(
            'base.group_user')
        cls.qc_user = cls._create_user(
            'qc_user',
            [cls.group_qc_user, cls.group_user],
            cls.company,
        )
        # User assigned to quality control manager group
        cls.qc_manager = cls.env.ref('base.user_root')

        # Create products
        cls.product_1 = cls.product.create({
            'name': 'Test Product 1',
            'type': 'product',
            'list_price': 100.0,
        })
        cls.product_2 = cls.product.create({
            'name': 'Test Product 2',
            'type': 'product',
            'list_price': 150.0,
        })

        # Create QC Team
        cls.team = cls.qc_team_obj._get_default_qc_team_id(
            user_id=cls.qc_user.id)

    @classmethod
    def _create_user(self, login, groups, company):
        """Create a user."""
        user = self.res_users.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'groups_id': [(6, 0, [group.id for group in groups])]
        })
        return user

    def test_01_create_qc_problem_group(self):
        """Test to create a QC problem group"""
        # QC Manager creates QC Problem group
        self.qc_problem_group = \
            self.qc_problem_grp_obj.sudo(self.qc_manager.id).create({
                'name': "QC Problem Group Test",
                'company_id': self.company.id,
            })

        # QC User tries to create QC Problem group
        with self.assertRaises(AccessError):
            self.qc_problem_grp_obj.sudo(self.qc_user.id).create({
                'name': "QC Problem Group Test",
                'company_id': self.company.id,
            })
        # QC User lists all QC Problem groups
        qc_problem_group_list = self.qc_problem_grp_obj. \
            sudo(self.qc_user.id).search([]).mapped('name')
        self.assertEquals(len(qc_problem_group_list), 1,
                          'User 2 should have read access '
                          'to all QC problem groups')

    def test_02_create_qc_problem(self):
        """Test to create a QC problem"""
        # Create first QC Problem Group
        qc_problem_group = \
            self.qc_problem_grp_obj.sudo(self.qc_manager.id).create({
                'name': "QC Problem Group Test",
                'company_id': self.company.id,
            })
        # QC Manager creates QC Problem
        self.qc_problem = \
            self.qc_problem_obj.sudo(self.qc_manager.id).create({
                'name': "QC Problem Test",
                'company_id': self.company.id,
                'problem_group_id': qc_problem_group.id,
            })

        # QC User creates QC Problem
        self.qc_problem_obj.sudo(self.qc_user.id).create({
            'name': "QC Problem Test 2",
            'company_id': self.company.id,
            'problem_group_id': qc_problem_group.id,
        })
        # QC User lists all QC Problem
        qc_problem_list = self.qc_problem_obj. \
            sudo(self.qc_user.id).search([]).mapped('name')
        self.assertEquals(len(qc_problem_list), 2,
                          'User 2 should have read access '
                          'to all QC problem')

    def test_03_create_qc_stage(self):
        """Test to create a QC stage"""
        # QC Manager creates QC Stage
        self.qc_stage = \
            self.qc_stage_obj.sudo(self.qc_manager.id).create({
                'name': "QC Stage Test",
                'team_id': self.team.id,
            })

        # QC User tries to create QC Stage
        with self.assertRaises(AccessError):
            self.qc_stage_obj.sudo(self.qc_user.id).create({
                'name': "QC Stage Test 2",
                'team_id': self.team.id,
            })
        # QC User lists all QC Stage
        qc_stage_list = self.qc_stage_obj. \
            sudo(self.qc_user.id).search([]).mapped('name')
        self.assertEquals(len(qc_stage_list), 3,
                          'User 1 should have read access '
                          'to all QC stages')

    def test_04_create_qc_issue(self):
        """Test to create a QC issue"""
        # QC Manager creates QC Issue
        self.qc_issue = \
            self.qc_issue_obj.sudo(self.qc_manager.id).create({
                'product_id': self.product_1.id,
                'product_qty': 1.0,
                'inspector_id': self.qc_manager.id,
                'product_uom': self.product_1.uom_id.id,
            })

        # QC User creates QC Issue
        self.qc_issue_2 = \
            self.qc_issue_obj.sudo(self.qc_user.id).create({
                'product_id': self.product_1.id,
                'product_qty': 1.0,
                'inspector_id': self.qc_user.id,
                'product_uom': self.product_1.uom_id.id,
            })
        # QC User lists all QC Issue
        qc_issue_list = self.qc_issue_obj. \
            sudo(self.qc_user.id).search([]).mapped('name')
        self.assertEquals(len(qc_issue_list), 2,
                          'User 2 should have read access '
                          'to all QC issues')

    def test_05_create_qc_issue_stage(self):
        """Test to create a QC issue stage"""
        # QC Manager creates QC Issue Stage
        self.qc_issue_stage = \
            self.qc_issue_stage_obj.sudo(self.qc_manager.id).create({
                'name': "QC Stage Test",
                'qc_team_id': self.team.id,
            })

        # QC User tries to create QC Issue Stage
        with self.assertRaises(AccessError):
            self.qc_issue_stage_obj.sudo(self.qc_user.id).create({
                'name': "QC Stage Test 2",
                'qc_team_id': self.team.id,
            })
        # QC User lists all QC Issue Stage
        qc_issue_stage_list = self.qc_issue_stage_obj. \
            sudo(self.qc_user.id).search([]).mapped('name')
        self.assertEquals(len(qc_issue_stage_list), 1,
                          'User 2 should have read access '
                          'to all QC stages')

    def test_06_write_qc_issue(self):
        """Test to write a QC issue stage"""
        # QC Manager creates QC Issue
        qc_issue = \
            self.qc_issue_obj.sudo(self.qc_manager.id).create({
                'product_id': self.product_1.id,
                'product_qty': 1.0,
                'inspector_id': self.qc_manager.id,
                'product_uom': self.product_1.uom_id.id,
            })

        # Change product
        qc_issue.sudo(self.qc_manager.id).write({
            'product_id': self.product_2.id,
            'product_uom': self.product_2.uom_id.id,
        })

        # Change quantity
        qc_issue.sudo(self.qc_manager.id).write({'product_qty': 2.0})

        # Change inspector
        qc_issue.sudo(self.qc_manager.id).write({
            'inspector_id': self.qc_user.id
        })

    def test_07_scrap_products(self):
        """Test scrapped products"""
        # QC Manager creates QC Issue
        qc_issue = \
            self.qc_issue_obj.sudo(self.qc_manager.id).create({
                'product_id': self.product_1.id,
                'product_qty': 1.0,
                'inspector_id': self.qc_manager.id,
                'product_uom': self.product_1.uom_id.id,
            })

        res = qc_issue.scrap_products()

        scrap = self.stock_scrap_obj.\
            with_context(res.get('context', {})).create({})

        scrap.action_validate()
        qc_issue.action_view_stock_scrap()

        self.assertEquals(qc_issue.stock_scrap_qty, 1,
                          "Scrap quantity should equal 1")
