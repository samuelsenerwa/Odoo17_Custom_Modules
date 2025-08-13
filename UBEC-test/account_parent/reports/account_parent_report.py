##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import api, fields, models


class ReportCoATemplate(models.AbstractModel):
    _name = "report.account_parent.account_parent_print_template"
    _description = "Chart of account Hierarchy Report"

    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': data.get('context', {}).get('active_model'),
            'data': data.get('data', {}),
        }