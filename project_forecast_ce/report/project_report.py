# -*- coding: utf-8 -*-


from odoo import fields, models, tools


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"


    forecast_hours = fields.Float("Forecast Hours", help='It is the time forecast to achieve the task.',readonly=True)
    forecast_percent = fields.Float("Forecast Percent", help='It is the time forecast to achieve the task in percent of planned.',readonly=True)

    def _select(self):
        return super(ReportProjectTaskUser,self)._select() + 
            """,
            t.total_hours_spent + t.remaining_hours as forecast_hours,
            t.remaining_hours / (t.planned_hours + t.remaining_hours) * 100 as forecast_percent,
            """

    # dEPENDS on planner_ce
    # ~ def _group_by(self):
        # ~ return super(ReportProjectTaskUser,self)._select() + 
            # ~ ",\nt.role as role"

 
