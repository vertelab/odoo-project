odoo.define("vertel_project_timeline.TimelineModel", function (require) {
    "use strict";

    const TimelineModel = require("web_timeline.TimelineModel");

    TimelineModel.include({
        _loadTimeline: function () {

            if (this.modelName == 'project.task') {
                this.data.domain = [['project_id', '=', 1]]
            }

            return this._rpc({
                model: this.modelName,
                method: "search_read",
                kwargs: {
                    fields: this.fieldNames,
                    domain: this.data.domain,
                    order: [{name: this.default_group_by}],
                    context: this.data.context,
                },
            }).then((events) => {
                this.data.data = events;
                this.data.rights = {
                    unlink: this.unlink_right,
                    create: this.create_right,
                    write: this.write_right,
                };
            })
        },
    });
});