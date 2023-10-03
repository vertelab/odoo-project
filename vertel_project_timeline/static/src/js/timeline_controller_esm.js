/** @odoo-module **/

import AbstractController from "@web_timeline/js/timeline_controller.esm";
import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import core from "web.core";
import Dialog from "web.Dialog";
var _t = core._t;
import {Component} from "@odoo/owl";


export default AbstractController.include({
    update: function (params, options) {
        const res = this._super.apply(this, arguments);
        if (_.isEmpty(params)) {
            return res;
        }
        const defaults = _.defaults({}, options, {
            adjust_window: true,
        });
        var domains = params.domain || this.renderer.last_domains || [];

        if (this.model.modelName == 'project.task') {
            domains = [['project_id', '=', 1]]
        }

        const contexts = params.context || [];
        const group_bys = params.groupBy || this.renderer.last_group_bys || [];
        this.last_domains = domains;
        this.last_contexts = contexts;
        // Select the group by
        let n_group_bys = group_bys;
        if (!n_group_bys.length && this.renderer.arch.attrs.default_group_by) {
            n_group_bys = this.renderer.arch.attrs.default_group_by.split(",");
        }
        this.renderer.last_group_bys = n_group_bys;
        this.renderer.last_domains = domains;

        let fields = this.renderer.fieldNames;
        fields = _.uniq(fields.concat(n_group_bys));

        $.when(
            res,
            this._rpc({
                model: this.model.modelName,
                method: "search_read",
                kwargs: {
                    fields: fields,
                    domain: domains,
                    order: [{name: this.renderer.arch.attrs.default_group_by}],
                },
                context: this.getSession().user_context,
            }).then((data) =>
                this.renderer.on_data_loaded(data, n_group_bys, defaults.adjust_window)
            )
        );
        return res;
    },
})