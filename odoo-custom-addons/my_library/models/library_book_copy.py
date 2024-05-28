from odoo import models, fields, api
class LibraryBookCopy(models.Model):
    _name = "library.book.copy"
    _inherit = "library.book"
    description = "Library Book's Copy"

# add the xml to see the views of the model