# Copyright (C) 2025: BizzAppDev Systems Pvt. Ltd.(https://www.bizzappdev.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2.errors import UniqueViolation

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestMrpTag(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MrpTag = cls.env["mrp.tag"]
        cls.parent_tag = cls.MrpTag.create({"name": "Parent Tag"})
        cls.child_tag = cls.MrpTag.create(
            {"name": "Child Tag", "parent_id": cls.parent_tag.id}
        )
        cls.unique_tag_name = "Unique Tag"
        cls.unique_tag = cls.MrpTag.create({"name": cls.unique_tag_name})

    def test_unique_tag_name(self):
        """Try to create a tag with the same name"""
        with self.assertRaises(UniqueViolation), mute_logger("odoo.sql_db"):
            self.MrpTag.create({"name": self.unique_tag_name})

    def test_parent_child_relationship(self):
        """Test parent-child relationship of tags."""
        self.assertEqual(self.child_tag.parent_id, self.parent_tag)
        self.assertIn(self.child_tag, self.parent_tag.child_ids)

    def test_display_name_computation(self):
        """Display name check"""
        self.assertEqual(
            self.child_tag.display_name,
            f"{self.parent_tag.name} / {self.child_tag.name}",
        )

    def test_search_display_name(self):
        """Search should include correct domain"""
        res = self.MrpTag._search_display_name("ilike", self.child_tag.name)
        self.assertIn(("name", "ilike", self.child_tag.name), res)

    def test_no_recursive_parent(self):
        """Ensure that setting a child as parent of its own parent raises UserError"""
        with self.assertRaises(UserError):
            self.parent_tag.write({"parent_id": self.child_tag.id})
