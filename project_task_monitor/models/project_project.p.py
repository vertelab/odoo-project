from datetime import datetime, timedelta 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.addons.project_task_monitor.models.project_task import DEFAULT_CODE
import logging

_logger = logging.getLogger(__name__)

class ProjectTaskMonitor(models.Model):
    _name = "project.task.monitor"
    _description = "Project Task Monitor"
    _order = "sequence desc"

    activity_type = fields.Many2one('mail.activity.type', string="Activity Type", help="")
    code = fields.Text(string='Code',default=DEFAULT_CODE)
    esc_user = fields.Selection(selection=[
        ('create_uid', 'Created by'),
        ('write_uid', 'Last Updated by'),
        ('project_id.user_id', 'Project Manager'),
        ('project_id.test_manager_id', 'Test Manager'),
        ('assigned', 'Assigned to')
    ], string='User')
    message = fields.Char(string='Message')
    new_stage_id = fields.Many2one('project.task.type', string="New Stage", help="")
    project_id = fields.Many2one('project.project', string="Project", help="")
    # ~ stage_id = fields.Many2one('project.task.type', string="Stage", help="",domain="[('id','in','project_id.type_ids')]")
    sequence = fields.Integer(string='Sequence')
    stage_id = fields.Many2one('project.task.type', string="Stage", help="")
    summary = fields.Char(string='Summary', size=64)
    trigger_date = fields.Selection(selection=[
        ('create_date', 'Created On'),
        ('date_assign', 'Assigning Date'),
        ('date_deadline', 'Deadline'),
        ('date_end', 'Ending Date'),
        ('date_last_stage_update', 'Last Stage Update'),
        ('write_date', 'Last Updated On')
    ], string='Date')
    trigger_days = fields.Integer(string='Days')
    trigger_type = fields.Selection(selection=[
        ('code', 'Code'),
        ('activity', 'Activity'),
        ('stage', 'Stage'),
        ('esc', 'Escalate'),
        ('archive', 'Archive'),
        ('message', 'Message')
    ], string='Type')
    trigger_info = fields.Char()

class Project(models.Model):
    _inherit = "project.project"

    test_manager_id = fields.Many2one(comodel_name='res.users', string="Test Manager", help="Responsible for test")
    task_monitor_ids = fields.One2many(comodel_name='project.task.monitor', inverse_name='project_id', string="Task Monitor", help="")

    def cron_monitor(self):
        today = fields.Date.context_today(self)
        for project in self.search([]):
            for task in project.task_ids:
                for monitor in project.task_monitor_ids:
                    # Check if monitor stage matches task stage
                    if monitor.stage_id and task.stage_id == monitor.stage_id:
                        task_date = getattr(task, monitor.trigger_date, None)
                        if not task_date:
                            continue
                        # Convert task_date if it is string to date
                        if isinstance(task_date, str):
                            try:
                                task_date = datetime.strptime(task_date, '%Y-%m-%d').date()
                            except Exception as e:
                                _logger.warning(f"Failed to parse date {task_date} for task {task.id}: {e}")
                                continue
                        compare_date = task_date + timedelta(days=monitor.trigger_days)
                        #TODO We need a mecanism to do this just once and still catch up for old tasks or changes in monitor rules
                        if today == compare_date:
                            task.monitor_trigger(monitor)
                        
