odoo.define('disable_project_task_kanban.project_kanban', function (require) {
    'use strict';

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var KanbanColumn = require('web.KanbanColumn');
    var view_registry = require('web.view_registry');
    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
         // YTI TODO: Should be transformed into a extend and specific to project
        _openRecord: function () {
            if (this.selectionMode !== true && this.modelName === 'project.project' &&
                this.$(".o_project_kanban_boxes a").length) {
                this._super.apply(this, arguments);
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});
