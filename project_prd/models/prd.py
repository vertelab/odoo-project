from datetime import datetime, timedelta 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import re
import html
from bs4 import BeautifulSoup

import logging

_logger = logging.getLogger(__name__)


from odoo import models, fields


class MermaidMixin(models.AbstractModel):
    _name = 'mermaid.mixin'
    _description = 'Mermaid Diagram Mixin'

    mermaid_editor = fields.Html(string="Editor", copy=False)
    mermaid_diagram = fields.Text(string="Diagram", compute='_compute_mermaid_diagram', copy=False)

    _mermaid_keywords = r"^(graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|flowchart|pie|journey|gantt|gitGraph)\b"


    def wrap_mermaid_in_pre(self, mermaid_editor):
        """
        Finds Mermaid diagrams in HTML content and wraps them inside <pre> tags.

        Args:
            mermaid_editor (str): The raw HTML content.

        Returns:
            str: Modified HTML with Mermaid diagrams wrapped in <pre>.
        """
        if not mermaid_editor:
            return ""

        soup = BeautifulSoup(mermaid_editor, "html.parser")

        # Check for existing pre tags with mermaid content
        if soup.find('pre', class_='mermaid'):
            return str(soup)

        # Find potential Mermaid blocks
        potential_blocks = [tag for tag in soup.find_all(["p", "div"])
                            if re.search(self._mermaid_keywords, tag.get_text().lstrip(), re.MULTILINE)]

        # Process each potential block
        for start_tag in potential_blocks:
            diagram_content = []
            siblings_to_remove = []
            current_tag = start_tag

            # Process starting tag
            for child in BeautifulSoup(str(current_tag), "html.parser").find_all(string=True):
                if child.strip():
                    diagram_content.append(html.unescape(str(child)))

            # Process potential siblings
            next_tag = current_tag.next_sibling
            while next_tag and hasattr(next_tag, 'name') and next_tag.name in ['p', 'div']:
                if re.search(self._mermaid_keywords, next_tag.get_text().lstrip(), re.MULTILINE):
                    break

                for child in BeautifulSoup(str(next_tag), "html.parser").find_all(string=True):
                    if child.strip():
                        diagram_content.append(html.unescape(str(child)))

                siblings_to_remove.append(next_tag)
                next_tag = next_tag.next_sibling

            # Create pre tag and replace original tag
            pre_tag = soup.new_tag("pre")
            pre_tag.string = "\n".join(diagram_content)
            pre_tag['class'] = 'mermaid'
            start_tag.replace_with(pre_tag)

            # Remove siblings that were processed
            for sibling in siblings_to_remove:
                sibling.extract()  # extract() is an alternative to decompose()

        return str(soup)

    @api.depends('mermaid_editor')
    def _compute_mermaid_editor(self):
        """
        Computes the Mermaid diagram text and wraps it in <pre> tags if needed.
        Only processes content that appears to be Mermaid diagrams.
        """
        for rec in self:
            # Skip empty content or when called from our own update
            if not rec.mermaid_editor:
                rec.mermaid_diagram = ""
                continue

            soup = BeautifulSoup(rec.mermaid_editor, "html.parser")

            # Check for existing pre tag with mermaid content
            pre_tag = soup.find('pre', class_='mermaid')
            if pre_tag:
                rec.mermaid_diagram = pre_tag.get_text()
                continue

            # Check if content appears to be mermaid format
            text_content = soup.get_text('\n', strip=True)
            if not re.search(self._mermaid_keywords, text_content, re.MULTILINE):
                rec.mermaid_diagram = ""
                continue

            # Extract text preserving structure and indentation
            text_content = soup.get_text('\n', strip=False).replace('\xa0', ' ')
            rec.mermaid_diagram = text_content

            # Wrap in pre tags
            wrapped_content = self.wrap_mermaid_in_pre(rec.mermaid_editor)
            if wrapped_content != rec.mermaid_editor:
                rec.mermaid_editor = wrapped_content

    mermaid_diagram = fields.Text(string="Diagram", compute=_compute_mermaid_editor, copy=False)

    


class ProductRequirementDocument(models.Model):
    _name = 'prd.document'
    _inherit = ['mermaid.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Product Requirement Document'

    duration_tracking = fields.Float(string='Duration Tracking')
    active = fields.Boolean(string='Active', default=True)
    parent_id = fields.Many2one(comodel_name='prd.document',string="Parent PRD",help="")
    company_id = fields.Many2one(comodel_name='res.company',string="Company",help="") 
    name = fields.Char(string="Titel", required=True)
    summary = fields.Char(string="Summary", required=True)
    description = fields.Text(string="Description",help="Purpuse")
    version = fields.Char(string="Version", default="1.0",readonly=True,tracking=True)
    author_id = fields.Many2one('res.users', string="Author",tracking=True)
    product_owner_id = fields.Many2one('res.users', string="Product Owner",tracking=True)
    approved_by_id = fields.Many2one('res.users', string="Approved By",readonly=True,tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today,readonly=True,tracking=True)
    goals = fields.Text(string="Goal")
    user_persona = fields.Text(string="Användarbeskrivning")
    use_cases = fields.Text(string="Användningsfall")
    success_criteria = fields.Text(string="Success Criteria")
    dependencies = fields.Text(string="Dependencies")
    risks = fields.Text(string="Risks")
    document_type = fields.Selection([
        ('module', 'Module'),
        ('other', 'Other')],
        string="Type",
        default='module',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="State",
        default='draft',
        tracking=True
    )
    requirement_ids = fields.One2many(comodel_name='prd.requirement',inverse_name='prd_id',string="Requirements",help="") 
    function_ids = fields.One2many(comodel_name='prd.function',inverse_name='prd_id',string="Functions",help="") 

    requirements_count = fields.Integer(string="Total Requirements", compute='_compute_requirements_counts')
    closed_requirements_count = fields.Integer(string="Closed Requirements", compute='_compute_requirements_counts')
    requirements_percentage = fields.Float(string="Requirements Completion %", compute='_compute_requirements_counts')

    functions_count = fields.Integer(string="Total Functions", compute='_compute_functions_counts')
    closed_functions_count = fields.Integer(string="Closed Functions", compute='_compute_functions_counts')
    functions_percentage = fields.Float(string="Functions Completion %", compute='_compute_functions_counts')

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'approved':
            self.approved_by_id = self.env.user.id
            self.date = fields.Date.today()
        else:
            self.approved_by_id = False

    @api.depends('function_ids')
    def _compute_functions_counts(self):
        for record in self:
            total = len(record.function_ids.filtered(lambda r: r.priority == 'should'))
            closed = len(record.function_ids.filtered(lambda f: f.state == 'done'))
            record.functions_count = total
            record.closed_functions_count = closed
            record.functions_percentage = (closed / total * 100) if total else 0.0

    @api.depends('requirement_ids')
    def _compute_requirements_counts(self):
        for record in self:
            total = len(record.requirement_ids.filtered(lambda r: r.priority == 'should'))
            closed = len(record.requirement_ids.filtered(lambda r: r.state == 'done'))  
            record.requirements_count = total
            record.closed_requirements_count = closed
            record.requirements_percentage = 0.0
            if total > 0:
                record.requirements_percentage = (closed / total) * 100


    def button_minor_version(self):
        for record in self:
            major, minor = record.version.split('.')
            # Increment minor
            minor = str(int(minor) + 1)
            record.version = f"{major}.{minor}"
            record.date = fields.Date.today()

    def button_major_version(self):
        for record in self:
            major, minor = record.version.split('.')
            # Increment major and reset minor to 0
            major = str(int(major) + 1)
            record.version = f"{major}.0"
            record.date = fields.Date.today()

    def action_functions(self):
      return {
          'type': 'ir.actions.act_window',
          'name': 'Functions',
          'res_model': 'prd.function',
          'domain': [('prd_id', '=', self.id)],
          'view_mode': 'list,form',
          'target': 'current',
      }

    def action_requirements(self):
      return {
          'type': 'ir.actions.act_window',
          'name': 'Requirements',
          'res_model': 'prd.requirement',
          'domain': [('prd_id', '=', self.id)],
          'view_mode': 'list,form',
          'target': 'current',
      }


class PrdFunction(models.Model):
    _name = 'prd.function'
    _inherit = ['mermaid.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'PRD Functions'


    # models / data / sequrity / sequirity.xml / views / 

    description = fields.Text(string="Description")
    input_data = fields.Text(string="Input")
    name = fields.Char(string="Name", required=True)
    odoo_view_ids = fields.Many2many(
        comodel_name='prd.odoo_view_type',
        string='View Types',
        help=""
    )
    output_data = fields.Text(string="Output")
    process_data = fields.Text(string="Process")
    priority = fields.Selection([
        ('must', 'Must'),
        ('should', 'Should'),
        ('could', 'Could')
    ], string="Priority", default='must')
    prd_id = fields.Many2one('prd.document', string='PRD', ondelete='cascade', required=True)
    prompt = fields.Text(string="Prompt")
    requirement_ids = fields.One2many(
        comodel_name='prd.requirement',
        inverse_name='prd_id',
        string="Requirements",
        help=""
    )
    action = fields.Text(string='Action')
    menu = fields.Text(string='Menu')
    sequence = fields.Integer(string='Sequence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done')
    ], string="State", default='draft')
    func_type = fields.Selection([
        ('app', 'App'),
        ('inherit', 'Addon'),
        ('settings', 'Settings'),
        ('ai_agent', 'AI Agent'),
        ('ai_quest', 'AI Quest'),
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('usability', 'Usability'),
    ], string="Type", default='app')
    user_id = fields.Many2one(comodel_name='res.users',string="Author",help="")
    
class OdooViewType(models.Model):
    _name = 'prd.odoo_view'
    _description = 'Odoo View'

    prd_id = fields.Many2one('prd.document', string='PRD', ondelete='cascade', required=True)
    view_type_id = fields.Many2one('prd.odoo_view_type', string='View Type', ondelete='cascade', required=True)
    prompt = fields.Text(string='Prompt')
    filename = fields.Char(string="Filename")
    source_code = fields.Text(string="Source Code")
    
    @api.onchange('view_type_id')
    def _onchange_view_type_id(self):
        if self.view_type_id:
            self.prompt = self.view_type_id.prompt or ''
        else:
            self.prompt = ''
    
    
class PrdRequirement(models.Model):
    _name = 'prd.requirement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PRD Requirement'

    description = fields.Text(string="Description")
    function_ids = fields.Many2many(
        comodel_name='prd.function',
        string='Functions',
        help="Functions that implement this requirement",
        compute='_compute_function_ids',
        store=True
    )
    prd_id = fields.Many2one('prd.document', string='PRD', ondelete='cascade', required=True)
    name = fields.Char(string="Name", required=True)
    priority = fields.Selection([
        ('must', 'Must'),
        ('should', 'Should'),
        ('could', 'Could')
    ], string="Priority", default='must')
    sequence = fields.Integer(string='Sequence')
    req_type = fields.Selection([
        ('func', 'Functional'),
        ('non-functional', 'Non Functional'),
    ], string="Type", default='func')
    user_id = fields.Many2one(comodel_name='res.users',string="Author",help="")
    no= fields.Char(string='No', trim=True, )
    category = fields.Char(string='Category', trim=True, )
    page = fields.Char(string='Page', trim=True, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done')
    ], string="State", default='draft')
    
    @api.depends('prd_id.function_ids')
    def _compute_function_ids(self):
        for requirement in self:
            functions = self.env['prd.function'].search([('requirement_ids', 'in', requirement.id)])
            requirement.function_ids = [(6, 0, [f.id for f in functions])]
    
    
class OdooViewType(models.Model):
    _name = 'prd.odoo_view_type'
    _description = 'Odoo View Type'

    name = fields.Char(string='View Type Name', required=True)
    code = fields.Char(string='View Type Code', required=True)
    description = fields.Text(string='Description')
    prompt = fields.Text(string='Prompt')
    active = fields.Boolean(string='Active', default=True)
