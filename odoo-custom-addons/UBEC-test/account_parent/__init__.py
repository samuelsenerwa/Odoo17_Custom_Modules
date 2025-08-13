##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from . import controllers
from . import models
from . import wizard
from . import reports


def _assign_account_parent(env):
    env['account.account']._parent_store_compute()
