# Adding hierarchy to a model

from odoo import models, fields, api


class BookCategory(models.Model):
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

    @api.constraints('parent_id')
    def _check_hierarchy(self):
        if not self.check_recursion():
            raise models.validationError(
                'Error! You cannot create recursive categories'
            )

    # assigning category to a book
    category_id = fields.Many2one('library.book.category')

    # add menus, view and security rules inorder to display he library.book.category model in the user interface
