/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";
import { download } from "@web/core/network/download";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { useSetupAction } from "@web/search/action_hook";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

function processLine(line) {
    return { ...line, lines: [], isFolded: true };
}

function extractPrintData(lines) {
    const data = [];
    for (const line of lines) {
        const { id, model_id, model, unfoldable, level } = line;
        data.push({
            id: id,
            model_id: model_id,
            model_name: model,
            unfoldable,
            level: level || 1,
        });
        if (!line.isFolded) {
            data.push(...extractPrintData(line.lines));
        }
    }
    return data;
}

export class CoaReport extends Component {
    static template = "account_parent.CoaReport";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
//        this.user = useService("user");

        onWillStart(this.onWillStart);
        useSetupAction({
            getLocalState: () => ({
                lines: [...this.state.lines],
                heading: this.state.heading,
                applied_filter: this.state.applied_filter,
            }),
        });

        this.state = useState({
            lines: this.props.state?.lines || [],
            heading: this.props.state?.heading || '',
            applied_filter: this.props.state?.applied_filter || false,
        });

        const { active_id, active_model, auto_unfold, context, url } =
            this.props.action.context;
        this.controllerUrl = url;

        this.context = context || {};
        Object.assign(this.context, {
            active_id: active_id || this.props.action.context.active_id,
            auto_unfold: auto_unfold || false,
            active_model: active_model || this.props.action.context.params?.active_model || false,
//            ttype: ttype || false,
        });
        this.display = {
            controlPanel: {},
            searchPanel: false,
        };
    }

    async onWillStart() {
        if (!this.state.lines.length) {
            const report_data = await this.orm.call("account.open.chart", "get_html", [
                this.context,
            ]);
            const mainLines = report_data.lines;
            const heading = report_data.heading;
            const applied_filter = report_data.applied_filter;
            this.state.lines = mainLines.map(processLine);
            this.state.heading = heading;
            this.state.applied_filter = applied_filter;
        }
    }

    async onClickBoundLink(line) {
        const ids = line.ids || [line.id];
        const action = await this.orm.call("account.open.chart", "show_journal_items", [
                line.wiz_id, ids, line.name
            ]);
        this.actionService.doAction(action);
    }
    async onClickPrint() {
        const action = await this.orm.call("account.open.chart", "btn_print_pdf", [
                this.context.active_id
            ]);
        this.actionService.doAction(action);
    }

    onClickXLSPrint() {
    //        const data = JSON.stringify(extractPrintData(this.state.lines));
        if (!this.controllerUrl){
            throw new Error('CoA Report not loaded')
        }

        const url = this.controllerUrl
            .replace(":active_id", this.context.active_id)
            .replace(":active_model", this.context.active_model)
            .replace("output_format", "xls");
        download({
            data: {  },
            url,
        });
    }


    async toggleLine(line) {
        line.isFolded = !line.isFolded;
        const ids = line.ids || [line.id];
        if (!line.lines.length) {
            line.lines = (
                await this.orm.call("account.open.chart", "get_lines", [line.wiz_id, line.id], {
                    model_id: line.model_id,
                    model_name: line.model,
                    acc_ids: ids,
                    level: line.level + 1 || 1,
                })
            ).map(processLine);
        }
    }
    async unfoldAllLines() {
        for (let line of this.state.lines) {
            await this.unfoldLineRecursively(line);
        }
        this.render();
    }

    async unfoldLineRecursively(line) {
        if (line.isFolded) {
            await this.toggleLine(line);
        }
        for (let subLine of line.lines) {
            await this.unfoldLineRecursively(subLine);
        }
    }
}

registry.category("actions").add("coa_hierarchy", CoaReport);


