/** @odoo-module **/

import { AccountTypeSelection } from "@account/components/account_type_selection/account_type_selection";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
//    const patchMixin = require("web.patchMixin");
//    const PatchableAttachment = patchMixin(Attachment);

//const {QWeb, Context} = owl;
patch(AccountTypeSelection.prototype, {
    get hierarchyOptions() {
        const opts = this.options;
        return [
            { name: _t('Balance Sheet') },
            { name: _t('Assets'), children: opts.filter(x => x[0] && x[0].startsWith('asset')) },
            { name: _t('Liabilities'), children: opts.filter(x => x[0] && x[0].startsWith('liability')) },
            { name: _t('Equity'), children: opts.filter(x => x[0] && x[0].startsWith('equity')) },
            { name: _t('Profit & Loss') },
            { name: _t('Income'), children: opts.filter(x => x[0] && x[0].startsWith('income')) },
            { name: _t('Expense'), children: opts.filter(x => x[0] && x[0].startsWith('expense')) },
            { name: _t('Other'), children: opts.filter(x => x[0] && ['off_balance','view'].includes(x[0])) },
        ];
    }

});



