# -*- coding: utf-8 -*-

from datetime import timedelta

import requests

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


# Using abstract models for reusable model features
class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


# Add fields to the model
class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Unavailable'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State', default="draft"
    )
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
                           help='Total book page count')
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),
    )
    author_ids = fields.Many2many(
        'res.partner',
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
    )

    # Adding computational field to calculate book's age since its release date
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=True
    )

    # basic serverside rendering
    # check whether state transition is allowed
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')
                   ]
        return (old_state, new_state) in allowed

    # method to change the state of some books to new state that is passed as an argument
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    #  method to change the book state by calling change_state
    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    # using try...cache block
    def post_to_webservice(self, data):
        try:
            req = requests.post('http://my-test-service.com', data=data, timeout=10)
            content = req.json()
        except IOError:
            error_msg = _("Something went wrong during data submission")
            raise UserError(error_msg)
        return content

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise ValidationError('Release date must be in the past')

    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        ondelete='set null'
    )
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )

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


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    published_book_ids = fields.One2many(
        'library.book', 'publisher_id',
        string='Published Books'
    )

    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books'
    )
    count_books = fields.Integer('Number of Authored Books',
                                 compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result


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
    date_of_birth = fields.Date('Date of Birth')
