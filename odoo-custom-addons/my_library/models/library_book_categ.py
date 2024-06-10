# Adding hierarchy to a model

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'

    name = fields.Char('Category')
    description = fields.Text('Description')
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

    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self.check_recursion():
            raise models.validationError(
                'Error! You cannot create recursive categories'
            )

    # add menus, view and security rules inorder to display he library.book.category model in the user interface
