# Adding hierarchy to a model

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    name = fields.Char('Category')
    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='restrict',
        index=True
    )
    child_ids = fields.One2many(
        'library.book.category',
        'parent_id',
        string='Child Categories'
    )
    # special hierarchy support
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'
    parent_path = fields.Char(index=True)

    # creating a new record
    def create_categories(self):
        categ1 = {
            'name': 'Child Category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'email': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        record = self.env['library.book.category'].create(parent_category_val)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self.check_recursion():
            raise models.validationError(
                'Error! You cannot create recursive categories'
            )



    # add menus, view and security rules inorder to display he library.book.category model in the user interface
