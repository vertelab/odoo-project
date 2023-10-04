odoo.define("vertel_project_timeline.TimelineModel", function (require) {
    "use strict";

    const TimelineModel = require("web_timeline.TimelineModel");

    TimelineModel.include({
        _loadTimeline: function () {

             var kwargs = {
                    fields: this.fieldNames,
                    domain: this.data.domain,
                    order: [{name: this.default_group_by}],
                    context: this.data.context,
             }
            if (this.modelName == 'project.task') {
                 kwargs['timeline'] = true
            }
            return this._rpc({
                model: this.modelName,
                method: "search_read",
                kwargs: kwargs,
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