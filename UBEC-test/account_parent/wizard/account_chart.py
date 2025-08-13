##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api, _
from odoo.tools import format_amount
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup
from odoo.tools.misc import get_lang


class OpenAccountChart(models.TransientModel):
	"""
	For Chart of Accounts
	"""
	_name = "account.open.chart"
	_description = "Account Open chart"

	company_id = fields.Many2one(
		'res.company',
		string='Company', required=True,
		default=lambda self: self.env.company)
	date_from = fields.Date(string='Start Date')
	date_to = fields.Date(string='End Date')
	target_move = fields.Selection(
		[('posted', 'All Posted Entries'), ('all', 'All Entries')],
		string='Target Moves', required=True,
		default='posted')
	display_account = fields.Selection(
		[('all', 'All'), ('movement', 'With movements')],
		# ('not_zero', 'With balance is not equal to 0'),
		string='Display Accounts', required=True,
		default='movement',
		help=(
			"`All`: All account will be displayed, `With Movements`: Only accounts "
			"that have a movement based on the conditions given"))
	unfold = fields.Boolean('Auto Unfold')
	report_type = fields.Selection(
		selection=[
			('account', 'CoA based on Accounts'),
			('account_type', 'CoA based on Account Type')],
		string='Report type',
		default='account',
		help="If you haven't configured parent accounts, then use 'Account Type'")
	show_initial_balance = fields.Boolean(string='Show Initial Balance')
	has_parent = fields.Boolean()

	@api.onchange('report_type')
	def onchange_report_type(self):
		account_env = self.env['account.account']
		if not account_env.search([
			*account_env._check_company_domain(self.company_id.id or False),
			('parent_id', '!=', False)], limit=1):
			self.has_parent = False
		else:
			self.has_parent = True

	@api.onchange('date_to')
	def onchange_date_to(self):
		if self.date_from and self.date_to and self.date_to < self.date_from:
			raise UserError(_('End date must be greater than start date!'))
	
	def _build_contexts(self):
		self.ensure_one()
		result = dict()
		result['state'] = self.target_move or ''
		result['display_account'] = self.display_account or 'all'
		result['date_from'] = self.date_from or False
		result['date_to'] = self.date_to or False
		result['report_type'] = self.report_type
		result['strict_range'] = True if result['date_from'] else False
		result['show_parent_account'] = True
		result['company_id'] = self.company_id.id  # or self.env.user.company_id.id
		result['active_id'] = self.id
		result['auto_unfold'] = self.unfold
		result['show_initial_balance'] = self.show_initial_balance
		return result
	
	@api.model
	def build_domain(self, wiz_id=None, account_ids=None, context=None):
		domain = []
		if not context:
			context = dict()
		if account_ids:
			if isinstance(account_ids, int) or len(account_ids) == 1:
				account = self.env['account.account'].browse(account_ids)
				if account.account_type in ['asset_receivable', 'liability_payable']:
					context.update({'search_default_group_by_partner': True})
				# account_ids = [account_ids]
			sub_accounts = self.env['account.account'].with_context(
				{'show_parent_account': True}).search([('id', 'child_of', account_ids)])
			context.update({'account_ids': sub_accounts})
			ml = self.env['account.move.line'].with_context(context)
			tables, where_clause, where_params = ml._query_get()
			query = 'SELECT "account_move_line".id FROM ' + tables + 'WHERE' + where_clause 
			self.env.cr.execute(query, tuple(where_params))
			ids = (x[0] for x in self.env.cr.fetchall())
			list_ids = list(ids)
			domain.append(('id', 'in', list_ids))
		return domain, context

	def account_chart_open_window(self):
		"""
		Opens chart of Accounts
		@return: dictionary of Open account chart window on given date(s)
		and all Entries or posted entries
		"""
		self.ensure_one()
		ap_url = (
			'/account_parent/output_format/account_parent?'
			'active_id=%s&amp;active_model=%s') % (self.id, 'account.open.chart')
		result = {
			'name': 'Chart of Account Hierarchy',
			'type': 'ir.actions.client',
			'tag': 'coa_hierarchy',
			'context': """
			{'url': '%s',
			'model': 'account.open.chart',
			'active_model': 'account.open.chart'}""" % ap_url

		}
		used_context = self._build_contexts()
		if 'company_ids' in used_context:
			company_ids = used_context['company_ids']
		else:
			company_ids = [self.company_id.id]
		if not self.env['account.account'].search([
				*self.env['account.account']._check_company_domain(company_ids),
				('parent_id', '!=', False)], limit=1) and self.report_type == 'account':
			result = self.env.ref('account.action_account_form').read([])[0]
		# else:
			# result = self.env.ref('account.action_account_form').read([])[0]
			# self.report_type = 'account_type'
		# lines = self.with_context(used_context).get_lines(
		# 	wiz_id=self.id)
		# if not lines:
		# 	raise ValidationError(
		# 		_('No Data to show. Please update the search options.'))
		
		if 'date_from' in used_context:
			del used_context['date_from']
		if 'date_to' in used_context:
			del used_context['date_to']
		
		result_context = safe_eval(result.get('context', '{}')) or {}
		used_context.update(result_context)
		result['context'] = str(used_context)
		return result

	@api.model
	def _amount_to_str(self, value, currency):
		return format_amount(self.env, value, currency)

	@api.model
	def _m2o_to_str(self, value):
		return self.env['ir.qweb.field.many2one'].value_to_html(value, {}) or ''

	@api.model
	def _selection_to_str(self, value, wiz):
		return self.env['ir.qweb.field.selection'].record_to_html(wiz, value, {}) or ''

	@api.model
	def _date_to_str(self, value):
		return self.env['ir.qweb.field.date'].value_to_html(value, {}) or ''

	@api.model
	def float_html_formatting(self, value, company):
		html_formatting = True
		if self._context.get('output_format', False) == 'xls':
			html_formatting = False
		return (
				html_formatting and self._amount_to_str(value, company.currency_id)
				or value)
		# return value # manged in view

	@api.model
	def get_accounts(self, account_ids, context):
		account_domain = [('company_ids', '=', context.get('company_id', False))]
		if account_ids:
			account_domain += [('parent_id', 'in', account_ids)]
		else:
			account_domain += [('parent_id', '=', False)]
		return self.env['account.account'].sudo().with_context(context).search(
			account_domain)
	
	def line_data(self, level, wiz_id, parent_id, account):
		account = account.with_company(account.company_ids)
		return {
			'id': account.id,
			'ids': list([account.id,]),
			'wiz_id': wiz_id,
			'level': level,
			'unfoldable': account.account_type == 'view' and True or False,
			'auto_unfold': self._context.get('auto_unfold', False),
			'model_id': account.id,
			'parent_id': parent_id,
			'code': account.code,
			'sort_code': account.code,
			'name': account.name,
			'ac_type': self._selection_to_str('account_type', account),
			'type': account.account_type,
			'currency': self._m2o_to_str(account.currency_id),
			'company': self._m2o_to_str(account.company_ids),
			'debit': self.float_html_formatting(account.debit, account.company_ids),
			'credit': self.float_html_formatting(account.credit, account.company_ids),
			'balance': self.float_html_formatting(account.balance, account.company_ids),
			'company_obj': account.company_ids,
			'show_initial_balance': self._context.get('show_initial_balance', False),
			'initial_balance': self.float_html_formatting(
				account.initial_balance, account.company_ids),
			'ending_balance': self.float_html_formatting(
				account.initial_balance + account.balance, account.company_ids),
			'db': account.debit,
			'cr': account.credit,
			'bal': account.balance,
			'ini_bal': account.initial_balance,
			'end_bal': account.initial_balance + account.balance
			}

	@api.model
	def _lines(self, wiz_id=None, line_id=None, level=1, obj_ids=[]):
		final_vals = []
		display_account = self._context.get('display_account', 'all')
		for account in obj_ids:
			if display_account == 'movement':
				if account.credit or account.debit:
					final_vals += [self.line_data(
						level, wiz_id=wiz_id, parent_id=line_id, account=account)]
			else:
				final_vals += [self.line_data(
					level, wiz_id=wiz_id, parent_id=line_id, account=account)]
			
		return final_vals
	
	@api.model
	def get_account_lines(self, wiz_id=None, parent_id=None, account_ids=[], level=1):
		accounts = self.get_accounts(account_ids, self._context)
		return self._lines(wiz_id, parent_id, level=level, obj_ids=accounts)
	
	def account_type_data(self):
		parent_account_types = [
			{
				'name': _('Balance Sheet'), 'id': -1, 'parent_id': False,
				'internal_group': ['asset', 'liability', 'equity'], 'atype': False},
			{
				'name': _('Assets'), 'id': -11, 'parent_id': -1,
				'internal_group': ['asset'], 'atype': False},
			{
				'name': _('Receivable'), 'id': -111, 'parent_id': -11,
				'account_type': ['asset_receivable'], 'atype': True},
			{
				'name': _('Bank and Cash'), 'id': -112, 'parent_id': -11,
				'account_type': ['asset_cash'], 'atype': True},
			{
				'name': _('Current Assets'), 'id': -113, 'parent_id': -11,
				'account_type': ['asset_current'], 'atype': True},
			{
				'name': _('Non-current Assets'), 'id': -114, 'parent_id': -11,
				'account_type': ['asset_non_current'], 'atype': True},
			{
				'name': _('Prepayments'), 'id': -115, 'parent_id': -11,
				'account_type': ['asset_prepayments'], 'atype': True},
			{
				'name': _('Fixed Assets'), 'id': -116, 'parent_id': -11,
				'account_type': ['asset_fixed'], 'atype': True},
			{
				'name': _('Liabilities'), 'id': -12, 'parent_id': -1,
				'internal_group': ['liability'], 'atype': False},
			{
				'name': _('Payable'), 'id': -121, 'parent_id': -12,
				'account_type': ['liability_payable'], 'atype': True},
			{
				'name': _('Credit Card'), 'id': -122, 'parent_id': -12,
				'account_type': ['liability_credit_card'], 'atype': True},
			{
				'name': _('Current Liabilities'), 'id': -123, 'parent_id': -12,
				'account_type': ['liability_current'], 'atype': True},
			{
				'name': _('Non-current Liabilities'), 'id': -123, 'parent_id': -12,
				'account_type': ['liability_non_current'], 'atype': True},
			{
				'name': _('Equity'), 'id': -13, 'parent_id': -1,
				'internal_group': ['equity'], 'atype': False},
			{
				'name': _('Equity'), 'id': -131, 'parent_id': -13,
				'account_type': ['equity'], 'atype': True},
			{
				'name': _('Current Year Earnings'), 'id': -132, 'parent_id': -13,
				'account_type': ['equity_unaffected'], 'atype': True},
			{
				'name': _('Profit & Loss'), 'id': -2, 'parent_id': False,
				'internal_group': ['income', 'expense'], 'atype': False},
			{
				'name': _('Income'), 'id': -21, 'parent_id': -2,
				'internal_group': ['income'], 'atype': False},
			{
				'name': _('Income'), 'id': -211, 'parent_id': -21,
				'account_type': ['income'], 'atype': True},
			{
				'name': _('Other Income'), 'id': -212, 'parent_id': -21,
				'account_type': ['income_other'], 'atype': True},
			{
				'name': _('Expense'), 'id': -22, 'parent_id': -2,
				'internal_group': ['expense'], 'atype': False},
			{
				'name': _('Expenses'), 'id': -221, 'parent_id': -22,
				'account_type': ['expense'], 'atype': True},
			{
				'name': _('Depreciation'), 'id': -222, 'parent_id': -22,
				'account_type': ['expense_depreciation'], 'atype': True},
			{
				'name': _('Cost of Revenue'), 'id': -223, 'parent_id': -22,
				'account_type': ['expense_direct_cost'], 'atype': True},
		]
		return parent_account_types

	@api.model
	def get_at_accounts(self, at_data, context):
		account_domain = [('company_ids', '=', context.get('company_id', False))]
		if not at_data['atype']:
			account_domain += [('internal_group', 'in', at_data['internal_group'])]
		else:
			account_domain += [('account_type', 'in', at_data['account_type'])]
		return self.env['account.account'].sudo().with_context(context).search(
			account_domain)

	def at_line_data(
			self, at_data, level, wiz_id=False, parent_id=False, accounts=False):
		if not accounts:
			accounts = self.env['account.account'].browse()
		total_credit = sum(accounts.mapped('credit'))
		total_debit = sum(accounts.mapped('debit'))
		total_balance = sum(accounts.mapped('balance'))
		total_initial_balance = sum(accounts.mapped('initial_balance'))
		total_ending_balance = total_initial_balance + total_balance
		company = self.env['res.company'].browse(self._context.get('company_id', False))
		data = at_data.copy()
		data.update({
			'show_initial_balance': self._context.get('show_initial_balance', False),
			'wiz_id': wiz_id,
			'level': level,
			'unfoldable': True,
			'auto_unfold': self._context.get('auto_unfold', False),
			'model_id': at_data['id'],
			'parent_id': parent_id,
			'code': at_data['name'].upper(),
			'sort_code': -1 * at_data['id'],
			'ac_type': 'View',
			'type': 'view',
			'currency': self._m2o_to_str(company.currency_id),
			'company': self._m2o_to_str(company),
			'company_obj': company,
			'debit': self.float_html_formatting(total_debit, company),
			'credit': self.float_html_formatting(total_credit, company),
			'balance': self.float_html_formatting(total_balance, company),
			'initial_balance': self.float_html_formatting(total_initial_balance, company),
			'ending_balance': self.float_html_formatting(total_ending_balance, company),
			'db': total_debit,
			'cr': total_credit,
			'bal': total_balance,
			'ini_bal': total_initial_balance,
			'end_bal':	total_ending_balance
			})
		return data

	def _at_lines(self, wiz_id, parent_id, level=1):
		context = self._context
		final_vals = []
		display_account = context.get('display_account', 'all')
		if not parent_id:
			parent_id = False
		at_datas = list(filter(
			lambda x: x['parent_id'] == parent_id, self.account_type_data()))
		for at_data in at_datas:
			accounts = self.get_at_accounts(at_data, context)
			if display_account == 'movement':
				if sum(accounts.mapped('credit')) or sum(accounts.mapped('debit')):
					final_vals += [self.at_line_data(
						at_data, level, wiz_id=wiz_id, parent_id=parent_id,
						accounts=accounts)]
			else:
				final_vals += [self.at_line_data(
					at_data, level, wiz_id=wiz_id, parent_id=parent_id,
					accounts=accounts)]
		if not at_datas:
			at_datas = list(filter(lambda x: x['id'] == parent_id, self.account_type_data()))
			for at_data in at_datas:
				accounts = self.get_at_accounts(at_data, context)
				final_vals += self._lines(wiz_id, parent_id, level=level, obj_ids=accounts)
		return final_vals
	
	@api.model
	def get_account_type_lines(self, wiz_id=None, parent_id=None, account_ids=[], level=1):
		return self._at_lines(wiz_id, parent_id, level=level)

	@api.model
	def get_lines(self, wiz_id=None, line_id=None, **kw):
		context = dict(self.env.context)
		report_obj = self
		if wiz_id:
			report_obj = self.browse(wiz_id)
			context.update(report_obj._build_contexts())
		report_obj = report_obj.with_context(context)
		level = 1
		acc_ids = [line_id]
		if kw:
			level = kw.get('level', 0)
			acc_ids = kw.get('acc_ids', [])
		report_type = context.get('report_type', 'account_type')
		if report_type == 'account':
			res = report_obj.get_account_lines(wiz_id, line_id, acc_ids, level)
		else:
			res = report_obj.get_account_type_lines(wiz_id, line_id, acc_ids, level)

		reverse_sort = False
		final_vals = sorted(res, key=lambda v: v['sort_code'], reverse=reverse_sort)
		return final_vals

	@api.model
	def get_all_lines(self, line_id=False, acc_ids=[], level=0):
		self.ensure_one()
		result = []
		for line in self.get_lines(self.id, line_id=line_id, acc_ids=acc_ids,level=level):
			result.append(line)
			acc_ids = line.get('ids') or [line['model_id']]
			if line['type'] == 'view':
				result.extend(self.get_all_lines(
					line_id=line['model_id'], acc_ids=acc_ids, level=line['level']+1))
		return result
	
	@api.model
	def get_pdf_lines(self):
		lines = self.get_all_lines()
		return lines

	def get_xls_title(self, user_context):
		company = self.env['res.company'].browse(user_context.get('company_id')).name
		date_from = user_context.get('date_from')
		date_to = user_context.get('date_to')
		move = user_context.get('target_move')
		if date_from:
			row_data = [
				['', '', '', '', '', '', ],
				['Company:', 'Target Moves:', 'Date from:', 'Date to:', ''],
				[company, move, date_from, date_to, ''],
				['', '', '', '', '', '', '', ]]
		else:
			row_data = [
				['', '', '', '', '', '', ],
				['Company:', 'Target Moves:', ''],
				[company, move, ''],
				['', '', '', '', '', '', '', ]]
		return row_data

	# def get_pdf(self, wiz_id):
	# 	report_obj = self.browse(wiz_id)
	# 	user_context = report_obj._build_contexts()
	# 	lines = report_obj.with_context(print_mode=True, **user_context).get_pdf_lines()
	# 	heading = self.get_heading(user_context)
	# 	base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
	# 	rcontext = {
	# 		'mode': 'print',
	# 		'base_url': base_url,
	# 		'company_id': report_obj.company_id,
	# 	}
	# 	user_context.update(rcontext)
	# 	report_obj = self.with_context(user_context)
	# 	# if not config['test_enable']:
	# 	# 	user_context['commit_assetsbundle'] = True
	# 	user_context.update(report_obj.generate_report_context(user_context))
	# 	body = self.env['ir.ui.view'].with_context(user_context)._render_template(
	# 		"account_parent.report_coa_hierarchy_print",
	# 		values=dict(
	# 			rcontext,
	# 			lines=lines,
	# 			heading=heading,
	# 			user_data=user_context,
	# 			report=report_obj,
	# 			context=report_obj),
	# 	)
	#
	# 	header = self.env['ir.actions.report']._render_template(
	# 		"web.internal_layout", values=rcontext)
	# 	header = self.env['ir.actions.report']._render_template(
	# 		"web.minimal_layout",
	# 		values=dict(
	# 			rcontext, subst=True, body=Markup(header.decode())))
	# 	return self.env['ir.actions.report']._run_wkhtmltopdf(
	# 		[body],
	# 		header=header.decode(),
	# 		landscape=True,
	# 		specific_paperformat_args={
	# 			'data-report-margin-top': 25, 'data-report-header-spacing': 25,
	# 			'data-report-margin-bottom': 12
	# 		}
	# 	)
	
	def get_heading(self, context):
		res = False
		if context.get('company_id'):
			res = "Chart of Account: %s" % self.env['res.company'].browse(
				context.get('company_id')).display_name
		return res

	def generate_report_context(self, user_context):
		rcontext = dict()
		rcontext['show_initial_balance'] = user_context.get('show_initial_balance')
		rcontext['date_from'] = self._date_to_str(user_context.get('date_from'))
		rcontext['date_to'] = self._date_to_str(user_context.get('date_to'))
		rcontext['target_move'] = self._selection_to_str('target_move', self)
		rcontext['display_account'] = self._selection_to_str('display_account', self)
		rcontext['report_type'] = self._selection_to_str('report_type', self)
		return rcontext

	def _get_html(self):
		# result = {}
		rcontext = {}
		# context = self.env.context
		lines = []
		heading = []
		if not self:
			return dict(lines=lines, heading=heading, applied_filter=rcontext)
		# wiz_obj = self.browse(context.get('active_id'))
		user_context = self._build_contexts()
		rcontext = self.generate_report_context(user_context)
		lines = self.with_context(user_context).get_lines(
			wiz_id=user_context.get('active_id'))
		heading = self.get_heading(user_context)
		return dict(lines=lines, heading=heading, applied_filter=rcontext)

	@api.model
	def get_html(self, given_context=None):
		res = self.browse()
		if (
				given_context.get('active_id') and
				given_context.get('active_model') == 'account.open.chart'):
			res = self.browse(given_context.get('active_id'))
		return res._get_html()

	@api.model
	def show_journal_items(self, wiz_id=None, line_id=None, acc_name=''):
		line_ids = list(line_id)
		context = dict(self.env.context)
		report_obj = self
		if wiz_id:
			report_obj = self.browse(wiz_id)
			context.update(report_obj._build_contexts())
		report_obj = report_obj.with_context(context)
		report_type = context.get('report_type', 'account_type')
		account_ids = list()
		if report_type == 'account_type' and line_ids[0] < 0:
			at_datas = list(
				filter(lambda x: x['parent_id'] == line_ids[0], report_obj.account_type_data()))
			for at_data in at_datas:
				accounts = report_obj.get_at_accounts(at_data, context)
				account_ids += accounts.ids
			if not at_datas:
				at_datas = list(
					filter(lambda x: x['id'] == line_ids[0], report_obj.account_type_data()))
				for at_data in at_datas:
					accounts = report_obj.get_at_accounts(at_data, context)
					account_ids += accounts.ids
		else:
			if line_ids:
				account_ids.extend(line_ids)
			account_ids += report_obj.get_accounts(line_ids, context).ids
		domain, context = report_obj.build_domain(
			wiz_id=wiz_id, account_ids=account_ids, context=context)
		return {
			'name': 'Journal Items (' + acc_name + ')',
			'type': 'ir.actions.act_window',
			'res_model': 'account.move.line',
			'domain': domain,
			'context': context,
			'views': [[False, 'list'], [False, 'form']],
			'view_type': "list",
			'view_mode': "form",
			'target': 'current'
		}

	@api.model
	def btn_print_pdf(self, wiz_id=None):
		context = dict(self.env.context)
		report_obj = self
		if wiz_id:
			report_obj = self.browse(wiz_id)
		user_context = report_obj._build_contexts()
		lines = report_obj.with_context(print_mode=True, **user_context).get_pdf_lines()
		heading = self.get_heading(user_context)
		user_context.update(report_obj.generate_report_context(user_context))
		return self.env.ref(
			'account_parent.account_parent_report_print').with_context(
			landscape=True).report_action(self, data=dict(
			lines=lines, heading=heading, user_data=user_context))

