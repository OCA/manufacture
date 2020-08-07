# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestMrpProject(common.TransactionCase):
    def setUp(self):
        super(TestMrpProject, self).setUp()
        self.product = self.env['product.product'].create({'name': 'Test'})
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.bom = self.env['mrp.bom'].create(
            {
                'product_id': self.product.id,
                'product_tmpl_id': self.product.product_tmpl_id.id,
            })
        self.production = self.env['mrp.production'].create(
            {
                'product_id': self.product.id,
                'product_qty': 1,
                'product_uom_id': self.uom_unit.id,
                'bom_id': self.bom.id,
            })
        self.task = self.env['project.task'].create({
            'name': "Test",
            'user_id': self.env.uid,
        })
        self.project = self.env['project.project'].create({
            'name': "Test project",
            'user_id': self.env.uid,
        })

    def test_project_full(self):
        self.assertFalse(self.production.project_id)
        self.production.action_assign()
        self.assertFalse(self.production.project_id)
        # project is auto-created only if: TODO SO has a linked analytic account?
        self.production.project_id = self.project
        self.assertEqual(self.production.project_id.production_count, 1)
        # start the MO (and this starts the first WO)
        self.assertFalse(self.production.project_id.task_ids)
        self.production.button_plan()
        self.assertEqual(len(self.production.project_id.task_ids),
                         len(self.production.workorder_ids))
        # Remove production to see if the project is not removed # todo if? when?
        project = self.production.project_id
        self.production.action_cancel()
        self.production.unlink()
        self.assertTrue(project.exists())

    # def test_preservation_project_with_works(self):
    #     self.production.action_assign()
    #     self.production.button_plan()
    #     work = self.env['account.analytic.line'].create({
    #         'task_id': self.production.project_id.task_ids[0].id,
    #         'name': 'Test work',
    #         'user_id': self.env.user.id,
    #         'hours': 1.0})
    #     # Remove production to see if the project is removed
    #     project = self.production.project_id
    #     self.production.action_cancel()
    #     self.production.unlink()
    #     self.assertTrue(project.exists())
    #     self.assertTrue(work.exists())

    def test_task_name(self):
        self.assertEqual(
            self.task.with_context(name_show_user=True).name_get()[0][1],
            "[%s] Test" % self.env.user.name)
