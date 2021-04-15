from odoo import api, models

chart_classes = {
    0: "level-0",
    1: "level-1",
    2: "level-2",
    3: "level-3",
    4: "level-4",
}


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _get_project_domain(self, project_id):
        domain = [("id", "=", project_id)]
        return domain

    def _get_project_data(self, title=None, level=0):
        return {
            "id": self.id,
            "name": self.name,
            "title": title,
            "className": chart_classes[level],
        }

    @api.model
    def _get_children_data(self, child_ids, level):
        children = []
        for _rec in child_ids:
            data = _rec._get_task_data(title="Task", level=level)
            project_child_ids = self.search(self._get_project_domain(_rec.id))
            if project_child_ids:
                data.update(
                    {
                        "children": self._get_children_data(
                            project_child_ids, (level + 1) % 5
                        )
                    }
                )
            children.append(data)
        return children

    @api.model
    def get_organization_data(self):
        # First get project
        project_id = self._context.get('project_id')
        domain = self._get_project_domain(project_id)
        top_project = self.search(domain, limit=1)
        data = top_project._get_project_data(title="Project")

        # If any child we fetch data recursively for childs of top employee
        # top_project_child_ids = self.search(self._get_project_domain(top_project.id))
        top_project_child_ids = top_project.task_ids
        if top_project_child_ids:
            data.update(
                {"children": self._get_children_data(top_project_child_ids, 1)}
            )
        return data


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _get_task_domain(self, task_id):
        domain = [("id", "=", task_id), ('parent_id', '=', False)]
        return domain

    def _get_task_data(self, title=None, level=0):
        return {
            "id": self.id,
            "name": self.name,
            "title": title,
            "className": chart_classes[level],
        }
