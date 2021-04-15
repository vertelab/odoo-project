odoo.define('project_wbs.project_task_chart_overview', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var ProjectChartOverview = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: 'ProjectTaskChartOverview',

        events: {
            "click .node": "_onClickNode",
        },

        init: function(parent, context) {
            this.orgChartData = {};
            this.actionManager = parent;
            this.parent_context = context.params.context || {};
            this.parent_context['project_id'] = context.context.active_ids[0];
            this._super(parent, context);
        },

        willStart: function() {
            var self = this;

            var def = this._rpc({
                model: "project.project",
                method: "get_organization_data",
                context: self.parent_context,
            }).then(function(res) {
                console.log("res", res)
                self.orgChartData = res;
                // return;
            });

            return Promise.all([def, this._super.apply(this, arguments)]);
        },

        start: function() {
            this.oc = this.$("#chart-container").orgchart({
                data: this.orgChartData,
                nodeContent: "title",
            });

            return this._super.apply(this, arguments);
        },

        _openProjectFormView: function(id) {
            var self = this;
            // Go to the employee form view
            self._rpc({
                model: "project.project",
                method: "get_formview_action",
                args: [[id]],
            }).then(function(action) {
                self.trigger_up("do_action", {action: action});
            });
        },

        _onClickNode: function(ev) {
            ev.preventDefault();
            this._openProjectFormView(parseInt(ev.currentTarget.id, 10));
        },

    });

    core.action_registry.add('project_task_chart_overview', ProjectChartOverview);

    return ProjectChartOverview;

});
