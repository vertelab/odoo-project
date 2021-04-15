from odoo import models, fields, api, _
import uuid


class ProjectProject(models.Model):
    _inherit = 'project.project'

    allow_versioning = fields.Boolean(string="Allow Versioning", copy=False)
    version_id = fields.Many2one('project.versioning.project', string="Project Version", copy=False)

    def version_project(self):
        if self.allow_versioning:
            self.env['project.versioning.project'].create({
                'name': self.name + '-' + str(fields.Datetime.now()),
                'project_id': self.id,
                'project_name': self.name,
                'user_id': self.user_id.id,
                'partner_id': self.partner_id.id,
                'privacy_visibility': self.privacy_visibility,
                'label_tasks': self.label_tasks,
                'task_ids': [(0, 0, {
                    'name': task.name + '-' + str(fields.Datetime.now()),
                    'task_id': task.id,
                    'task_name': task.name,
                    'date_deadline': task.date_deadline,
                    'date_last_stage_update': task.date_last_stage_update,
                    # 'note': task.note,
                    'parent_id': task.parent_id.id,
                    'priority': task.priority,
                    'sequence': task.sequence,
                    'tag_ids': task.tag_ids.ids,
                    'kanban_state': task.kanban_state,
                    'color': task.color,
                    'user_email': task.user_email,
                    'subtask_project_id': task.subtask_project_id.id,
                    'email_from': task.email_from,
                    'email_cc': task.email_cc,
                    'description': task.description,
                    'project_id': task.project_id.id
                }) for task in self.task_ids]
            })

    @api.onchange('version_id')
    def onchange_version_id(self):
        if self.version_id:
            self.write({
                'name': self.version_id.project_name,
                'user_id': self.version_id.user_id.id,
                'partner_id': self.version_id.partner_id.id,
                'privacy_visibility': self.version_id.privacy_visibility,
                'label_tasks': self.version_id.label_tasks
            })

    # def write(self, vals):
    #     res = super(ProjectProject, self).write(vals)
    #     if res and self.allow_versioning:
    #         self.env['project.versioning.project'].create({
    #             'name': self.name + '-' + str(fields.Datetime.now()),
    #             'project_id': self.id,
    #             'project_name': self.name,
    #             'user_id': self.user_id.id,
    #             'partner_id': self.partner_id.id,
    #             'privacy_visibility': self.privacy_visibility,
    #             'label_tasks': self.label_tasks
    #         })
    #     return res


class ProjectTask(models.Model):
    _inherit = 'project.task'

    allow_versioning = fields.Boolean(string="Allow Versioning")
    version_id = fields.Many2one('project.versioning.task', string="Task Version", readonly=True)

    def version_project_task(self):
        self.env['project.versioning.project'].create({
            'name': self.project_id.name + '-' + str(fields.Datetime.now()),
            'project_id': self.project_id.id,
            'project_name': self.project_id.name,
            'user_id': self.project_id.user_id.id,
            'partner_id': self.project_id.partner_id.id,
            'privacy_visibility': self.project_id.privacy_visibility,
            'label_tasks': self.project_id.label_tasks,
            'task_ids': [(0, 0, {
                'name': task.name + '-' + str(fields.Datetime.now()),
                'task_id': task.id,
                'task_name': task.name,
                'date_deadline': task.date_deadline,
                'date_last_stage_update': task.date_last_stage_update,
                'parent_id': task.parent_id.id,
                'priority': task.priority,
                'sequence': task.sequence,
                'tag_ids': task.tag_ids.ids,
                'kanban_state': task.kanban_state,
                'color': task.color,
                'user_email': task.user_email,
                'subtask_project_id': task.subtask_project_id.id,
                'email_from': task.email_from,
                'email_cc': task.email_cc,
                'description': task.description,
                'project_id': task.project_id.id
            }) for task in self.project_id.task_ids]
        })

        # if self.allow_versioning:
        #     self.env['project.versioning.task'].create({
        #         'name': self.name + '-' + str(fields.Datetime.now()),
        #         'project_id': self.project_id.id,
        #         'user_id': self.user_id.id,
        #         'partner_id': self.partner_id.id,
        #         'date_assign': self.date_assign,
        #         'date_last_stage_update': self.date_last_stage_update,
        #         'sequence': self.sequence,
        #         'kanban_state': self.kanban_state,
        #         'priority': self.priority,
        #         'stage_id': self.stage_id.id,
        #         'description': self.description,
        #         'task_id': self.id,
        #         'task_name': self.name
        #     })
