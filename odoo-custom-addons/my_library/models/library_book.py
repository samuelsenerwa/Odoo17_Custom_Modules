# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

import requests
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

from odoo import models, fields, api

logger = logging.getLogger(__name__)


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
    manager_remarks = fields.Text('Manager Remarks')
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
    isbn = fields.Char('ISBN')
    old_edition = fields.Many2one('res.partner', string="Authors")
    short_name = fields.Char('Short Title', translate=True, index=True, required=True)
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count')
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),
                                 )
    author_ids = fields.Many2many('res.partner', string='Authors')
    cost_price = fields.Float('Book Cost')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price')

    # Adding computational field to calculate book's age since its release date
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=True
    )

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
        return True

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

    # obtaining record set
    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    # updating recordset values
    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    # search for records
    def find_book(self):
        domain = [
            '|'
            '&', ('name', 'ilike', 'Book Name'),
            ('category_id.name', 'ilike', 'Category Name'),
            '&', ('name', 'ilike', 'Book Name 2'),
            ('category_id.name', '=', 'Category Name 2')
        ]
        books = self.search_count(domain)
        logger.info('Books not found: %s', books)
        return True

    def find_partner(self):
        PartnerObj = self.env['res.partner']
        domain = [
            '&', ('name', 'ilike', 'Parth Gajjar'),
            ('company_id.name', '=', 'Odoo')
        ]
        partner = PartnerObj.searh(domain)

    # combining record sets

    # filtering recordset
    def filter_books(self):
        all_books = self._search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Book: %s', filtered_books)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
            return False

        return all_books.filter(predicate)

    # traversing recordset relations
    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Book Authors: %s', books_authors)

    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')

    # sorting record set
    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)

    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='release_date')

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
        ondelete='set null',
        context={},
        domain=[],
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

    # extend using create()
    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify'
                    'manager_remarks'
                )
        return super(LibraryBook, self).create(values)

    #     extend the write()
    def write(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify'
                    'manager_remarks'
                )
        return super(LibraryBook, self).write(values)


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
        """ This method used to customize display name of the record """
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = "%s (%s)" % (book.name, ','.join(authors))
            result.append(book.id, name)
        return result

    # how the user searches for a book
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     ]
            return super(LibraryBook, self)._name_search(
                name=name, args=args, operator=operator,
                limit=limit, name_get_uid=name_get_uid
            )

    # extracting grouped results using read_group()
    def grouped_data(self):
        data = self._get_average_cost()
        logger.info("Grouped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', '!=', False)],  # Domain
            ['category_id', 'cost_price:avg'],  # Fields to access
            ['category_id']  # group_by
        )
        return grouped_result


class BookCategory(models.Model):
    _name = 'library.book.category'

    name = fields.Char('Category')
    description = fields.Text('Description')


class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Library Member"

    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade',
        delegate=True
    )
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of Birth')
