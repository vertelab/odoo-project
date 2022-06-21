# -*- coding: utf-8 -*-
from operator import itemgetter
import re

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict, defaultdict
from odoo.addons.website.controllers.main import QueryURL
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR


class ProjectWCAGeController(http.Controller):

    @http.route(['/wcag-projects', '/wcag-projects/page/<int:page>'], type='http', auth="public", website=True)
    def is_wcag_projects(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = CustomerPortal._prepare_portal_layout_values(self)
        Project = request.env['project.project'].sudo()
        domain = [('is_wcag', '=', True)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # projects count
        project_count = Project.search_count(domain)
        # pager
        pager = portal_pager(
            url="/wcag-projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_count,
            page=page,
            step=CustomerPortal._items_per_page
        )

        # content according to pager and archive selected
        projects = Project.search(domain, order=order, limit=CustomerPortal._items_per_page, offset=pager['offset'])
        request.session['my_projects_history'] = projects.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'wcag_projects': projects,
            'page_name': 'wcag_project',
            'default_url': '/wcag-projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("website_project_wcag.is_wcag_projects", values)

    @http.route(['/wcag-projects/<int:project_id>/tasks', '/wcag-projects/<int:project_id>/tasks/page/<int:page>'], type='http', auth="public", website=True)
    def is_wcag_project_tasks(self, page=1, project_id=None, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = CustomerPortal._prepare_portal_layout_values(self)

        domain = [('project_id', '=', project_id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        if not sortby:
            sortby = 'date'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            domain += search_domain

        # task count
        task_count = request.env['project.task'].sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/wcag-projects/<int:project_id>/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=CustomerPortal._items_per_page
        )

        tasks = request.env['project.task'].sudo().search(domain, limit=CustomerPortal._items_per_page,
                                                          offset=pager['offset'])
        request.session['my_tasks_history'] = tasks.ids[:100]

        grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'wcag_project': request.env['project.project'].sudo().browse(project_id),
            'page_name': 'wcag_task',
            'default_url': '/wcag-projects/<int:project_id>/tasks',
            'pager': pager,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render("website_project_wcag.is_wcag_project_tasks", values)

    @http.route(['/wcag-project-task/<int:task_id>/wcags', '/wcag-project-task/<int:task_id>/wcags/page/<int:page>'],
                type='http', auth="public", website=True)
    def project_task_wcags(self, page=1, task_id=None, date_begin=None, date_end=None, sortby=None, filterby=None,
                              search=None, search_in='all', groupby=None, **kw):
        values = CustomerPortal._prepare_portal_layout_values(self)

        domain = [('task_id', '=', task_id)]

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        if not sortby:
            sortby = 'wcag_state'

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [('display_wcag_name', 'ilike', search)]])
            domain += search_domain

        # task count
        task_wcag_count = request.env['project.task.wcag'].sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/wcag-project-task/%s/wcags" % task_id,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby, 'search_in': search_in, 'search': search},
            total=task_wcag_count,
            page=page,
            step=CustomerPortal._items_per_page
        )

        wcag = request.env['project.task.wcag'].sudo().search(domain, limit=CustomerPortal._items_per_page, offset=pager['offset'])
        request.session['my_wcag_history'] = wcag.ids[:100]

        grouped_tasks = [wcag]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'wcags': wcag,
            'wcag_project': request.env['project.task'].sudo().browse(task_id).project_id,
            'wcag_task': request.env['project.task'].sudo().browse(task_id),
            'page_name': 'task_wcags',
            'default_url': '/wcag-project-task/%s/wcags' % task_id,
            'pager': pager,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render("website_project_wcag.project_task_wcags", values)



    @http.route(['/wcag-projects/<int:project_id>/wcag-task-overview', '/wcag-projects/<int:project_id>/wcag-task-overview/page/<int:page>'],
                type='http', auth="public", website=True)
    def project_task_wcags_overview(self, page=1, project_id=None, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = CustomerPortal._prepare_portal_layout_values(self)

        task_domain = [('project_id', '=', project_id)]

        wcag_rule = request.env['wcag.rule'].sudo().search([], order='display_wcag_name asc')

        tasks = request.env['project.task'].sudo().search(task_domain, order='name asc')
        tasks_list = []

        for task in tasks:
            task_wcag_ids = task.mapped('task_wcag_ids').filtered(lambda r: r.wcag_id in wcag_rule).sorted(key=lambda r: r.wcag_id.display_wcag_name)
            tasks_list.append(task_wcag_ids)

        values.update({
            'wcags': wcag_rule,
            'tasks': tasks_list,
        })


        return request.render("website_project_wcag.project_task_wcag_overview", values)


    
    @http.route(['/wcag-project-task/<int:task_id>/wcag/<int:wcag_id>'], type='http', auth="public", website=True)
    def view_project_task_wcag(self, task_id=None, wcag_id=None, **kw):
        values = CustomerPortal._prepare_portal_layout_values(self)

        wcag_domain = [('id', '=', wcag_id)]

        wcag = request.env['project.task.wcag'].sudo().search(wcag_domain, limit=1)

        values.update({
            'wcag': wcag,
            'page_name': 'task_wcag',
        })
        return request.render("website_project_wcag.wcag_details", values)
