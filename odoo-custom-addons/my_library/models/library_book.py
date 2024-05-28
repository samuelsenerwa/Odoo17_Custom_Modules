# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.odoo import api


# add fields to the model
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('lost', 'Lost')
         ],
        'State', default="draft"
    )
    # assigning category to a book
    category_id = fields.Many2one('library.book.category')
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', translate=True, index=True, required=True)
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_depender=False
                           )
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),  # optional precision decimal
    )
    author_ids = fields.Many2many(
        'res.partners',
        string='Authors'
    )
    cost_price = fields.Float(
        'Book Cost', digits='Book Price'
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency'
    )
    retail_price = fields.Monetary(
        'Retail Price',
        # optional: currency_field='currency_id',
    )

    # adding computational field to calculate book since it's release date
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        strore=False,  # optional
        compute_sudo=True  # optional
    )

    # adding the method with the value computation logic
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    # added a method and implemented the logic to write on computed field
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    # logic to search in computed field
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        #     convert the operator
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    # Adding constraint validation to a model

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)',
         'Book title must be unique.'
         ),
        ('positive_page', 'CHECK(pages>0)',
         'No of pages must be positive'
         )
    ]

    # python constraint
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past'
                )

    # using res.partner for many2one field to find books pubisher
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )
    # adding the related field to publisher's id
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )

    # adding dynamic relations using reference fields
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')
        ])
        return [(x.model, x.name) for x in models]

    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document'
    )

    # extend and inherit partner model


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'
    published_book_ids = fields.One2many(
        'library.book', 'publisher_id',
        string='Published Books'
    )

    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        #     relation='library_books_res_partner_rel' # optional
    )
    count_books = fields.Integer('Number of Authored Books',
                                 compute='_compute_count_books')

    # method to compute the book count
    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

    #     add a release date in the record's name


def name_get(self):
    result = []
    for record in self:
        rec_name = "%s (%s)" % (record.name, record.date_release)
        result.append((record.id, rec_name))
        return result


# delegation inheritance
class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade',
        delegate=True
    )
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')

# class my_library(models.Model):
#     _name = 'my_library.my_library'
#     _description = 'my_library.my_library'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
