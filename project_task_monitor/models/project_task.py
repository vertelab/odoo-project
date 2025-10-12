# -*- coding: utf-8 -*-
from dateutil import tz as timezone
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, AccessError
import datetime
import logging
import time

_logger = logging.getLogger(__name__)

DEFAULT_CODE = """
# Available variables:
#  - env: environment on which the action is triggered
#  - task: record on which the action is triggered
#  - stage: record on which the action is triggered
#  - self: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - _logger: _logger.info(message): logger to emit messages in server logs
#  - post_message: post_message('Message in chatter')
#  - UserError: exception class for raising user-facing warning messages
# To return an action, assign: action = {...}

"""
_logger = logging.getLogger(__name__)

def log(message, level="info", env=None):
    # Spara log i ir.logging-tabellen
    env = env or None
    if env:
        env['ir.logging'].create({
            'name': 'stage_code',
            'type': level,
            'dbname': env.cr.dbname,
            'level': level,
            'message': message,
            'path': 'project.task.type',
            'func': 'stage_code',
            'line': '0',
        })
    _logger.log(getattr(logging, level.upper(), logging.INFO), message)

class TaskType(models.Model):
    _inherit = "project.task.type"

    activity_type = fields.Many2one(comodel_name='mail.activity.type', string="Activity Type", help="")
    code = fields.Text(string='Code', default=DEFAULT_CODE)
    esc_user = fields.Selection(selection=[
        # ~ ('assigned','Assigned to')
        ('create_uid','Created by'),
        ('project_id.test_manager_id','Test Manager'),
        ('project_id.user_id','Project Manager'),
        ('write_uid','Last Updated by'),], string='User')
    message = fields.Char(string='Message')
    summary = fields.Char(string='Summary', size=64, trim=True)
    trigger_type = fields.Selection(selection=[
        ('activity','Activity'),
        ('archive','Archive'),
        ('code','Code'),
        ('esc','Escalate'),
        ('message','Message')], string='Type')

class Task(models.Model):
    _inherit = "project.task"

    @api.model
    def _execute_stage_code(self, stage, task):
        if not stage.code:
            return

        def post_message(body, **kwargs):
            """
                Writes an entry in the chatter/log directly on the task.
                Parameters:
                  - body: text for the message (str)
                  - subject, subtype_xmlid, message_type etc can be specified via kwargs.
            """
            task.message_post(body=body, **kwargs)

        local_ctx = {
            'env': self.env,
            'task': task,
            'stage': stage,
            'self': self,
            'time': time,
            'datetime': datetime,
            'dateutil': timezone,
            'timezone': timezone,
            'log': lambda message, level='info': log(message, level, self.env),
            '_logger': _logger,
            'UserError': UserError,
            'post_message': post_message,
            'action': None,
        }

        try:
            eval(stage.code, {}, local_ctx)
            if local_ctx.get('action'):
                return local_ctx['action']
        except Exception as e:
            _logger.error(f"Stage code execution failed: {e}")
            raise UserError(f"Error running code in stage: {e}")

    def write(self, vals):
        result = super().write(vals)
        if 'stage_id' in vals:
            for task in self:
                self.monitor_trigger(task.stage_id)
        return result
        
    def action_monitor(self):
        today = fields.Date.context_today(self)
        for task in self:
            for monitor in task.project_id.task_monitor_ids:
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
                    # This is manually started
                    #TODO We need a mecanism to do this just once and still catch up for old tasks or changes in monitor rules
                    if monitor.trigger_days > 0 and today >= compare_date:
                        task.monitor_trigger(monitor)

        
    def monitor_trigger(self,stage):
        for task in self:
            if hasattr(stage, 'code') and stage.code and stage.trigger_type == 'code':
                self._execute_stage_code(stage, task)
            if stage.trigger_type == 'activity':
                for user in task.user_ids:
                    self.env['mail.activity.schedule'].create({
                        'activity_type_id': stage.activity_type.id,
                        'activity_user_id': user.id,
                        'summary': stage.summary,
                        })
            elif stage.trigger_type == 'esc':
                if stage.esc_user == 'create_uid':
                    task.user_ids = [(6, 0, [task.create_uid.id])]
                    task.date_assign = fields.Date.context_today(self)
                elif stage.esc_user == 'write_uid':
                    task.user_ids = [(6, 0, [task.write_uid.id])]
                    task.date_assign = fields.Date.context_today(self)
                elif stage.esc_user == 'project_id.user_id' and task.project_id.user_id:
                    task.user_ids = [(6, 0, [task.project_id.user_id.id])]
                    task.date_assign = fields.Date.context_today(self)
                elif stage.esc_user == 'project_id.test_manager_id' and task.project_id.test_manager_id:
                    task.user_ids = [(6, 0, [task.project_id.test_manager_id.id])]
                    task.date_assign = fields.Date.context_today(self) 
            elif stage.trigger_type == 'archive':
                task.active = False
            elif stage.trigger_type == 'message':
                task.message_post(body=stage.message,)
