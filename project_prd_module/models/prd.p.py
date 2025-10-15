from datetime import datetime, timedelta 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ProductRequirementDocument(models.Model):
    _inherit = 'prd.document'
    
    sequence = fields.Integer(string="Sequence",)
    app_module = fields.Many2one(compdel_name="prd.odoo_module",string="App Module",)
    app_project = fields.Many2one(comodel_name='prd.odoo_project',string="App Project",help="")
    app_tree = fields.Char(string="Branch Tree", default="14.0")
    app_icon = fields.Image(string="Icon")    
    app_url = fields.Char(string="Website", compute="_get_app_url", default="vertel")
    app_banner = fields.Image(string="App Banner")
    app_summary = fields.Char(string="App Summary")
    app_category = fields.Many2one('ir.module.category', string="Category", default=1)
    app_description = fields.Text(string="App Description", default="The module description goes here.")
    app_manifest = fields.Char(string="App Manifest")
    app_license = fields.Char(string="App License", default="LGPL-3")
    # ~ app_index = fields.Html(string="App Index", translate=html_translate, sanitize_attributes=False,sanitize_form=False, default=_default_description)
    app_index = fields.Html(string="App Index", )
    app_depends = fields.Many2many(comodel_name='prd.odoo_module',string='Dependensies',help="") # relation|column1|column2

    def button_export_module(self):
        for prd in self:
            pass


    @api.depends('app_module','app_project')
    def _get_app_url(self):	 
        for b in self:
            if b.app_module:
               b.app_url = "https://vertel.se/apps/"+b.app_project.name+"/"+b.app_module.name
            else:
                b.app_url = False

    def sync_module(self):
        git_url = self.env['ir.config_parameter'].sudo().get_param('GitHubBaseUrl')
        raw_git_url = self.env['ir.config_parameter'].sudo().get_param('RawGitHubBaseUrl')

        if not raw_git_url:
            raise UserError(_("Raw Git URL is not set"))
        if not git_url:
            raise UserError(_("Git URL is not set"))
        if not self.app_project:
            raise UserError(_("No Git Project was specified"))
        if not self.app_module:
            raise UserError(_("No Module was specified"))
        for module in self:
            if not module.app_project:
                raise UserError(_("No Git Project was specified %s" % module.name))
            if not module.app_module:
                raise UserError(_("No Module was specified %s" % module.name))
            if not module.app_tree:
                raise UserError(_("No Module Tree was specified %s" % module.name))
            if module.app_project and module.app_module:
                module_url = f"{git_url}/{module.app_project}/tree/{module.app_tree}/{module.app_module}"
                raw_module_url = f"{raw_git_url}/{module.app_project}/{module.app_tree}/{module.app_module}"
                # get icon
                _logger.warning("--------->> module_url: %s" % module_url )
                _logger.warning("--------->> raw_module_url: %s" % raw_module_url )

                icon_data, icon_name = module._wget_sync(f"{raw_module_url}/static/description/icon.png")
                if icon_data and icon_name:
                    module.app_icon = module._create_attachment(icon_data, icon_name)
                # get banner
                manifest_obj = urllib.request.urlopen(f"{raw_module_url}/__manifest__.py").read().decode('utf-8')
                manifest = re.sub(r'(?m)^ *#.*\n?', '', manifest_obj)
                if manifest:
                    manifest = ast.literal_eval(manifest)
                    manifest_images = manifest.get('images')
                    if manifest_images:
                        main_screenshot = [image for image in manifest_images if image.endswith('_screenshot.png' or 'banner.png')]
                        banner_data, banner_name = self._wget_sync(
                            f"{raw_module_url}{main_screenshot[0] if main_screenshot else manifest_images[0]}"
                        )
                        if banner_data and banner_name:
                            module.app_banner = module._create_attachment(banner_data, banner_name)

                # manifest file
                module._sync_manifest(f"{raw_module_url}/__manifest__.py")

    def _sync_manifest(self, manifest_url):
        try:
            manifest_obj = urllib.request.urlopen(manifest_url).read().decode('utf-8')
            manifest = re.sub(r'(?m)^ *#.*\n?', '', manifest_obj)
            if manifest:
                manifest = ast.literal_eval(manifest)
                self.app_license = manifest.get('license')
                self.app_summary = manifest.get('summary')
        except Exception as e:
            _logger.warning("".join(traceback.format_exc()))
            return None, None

    def _wget_sync(self, url):
        _logger.warning(f"{url=}")
        try:
            file_obj = urllib.request.urlopen(url)
            _logger.warning(f"{file_obj=}")
            file_name = os.path.basename(url)
            _logger.warning(f"{file_name=}")
            return file_obj, file_name
        except Exception as e:
            _logger.warning("".join(traceback.format_exc()))
            return None, None

    def _create_attachment(self, datas, name):
        return base64.encodebytes(datas.read())

    def create_manifest(self):
        manifest_vals = {
            'name': self.name,
            'category': self.app_category.name,
            'website': 'https://vertel.se/apps/project/module',
            'summary': self.app_summary,
            'author': 'Vertel AB',
            'version': '14.0.0.0.1',
            'license': self.app_license,
            'description': self.app_description,
            'depends': [],
            'data': [],
            'installable': True,
            'application': True,
            'qweb': []
        }
        user_encode_data = json.dumps(manifest_vals, indent=2).encode('utf-8')
        temp = tempfile.NamedTemporaryFile(mode='w+b')
        temp.write(user_encode_data)
        temp.seek(0)
        attachment_id = self.env['ir.attachment'].create({
            'name': '__manifest__.py',
            'res_name': self.name,
            'res_model': self._name,
            'res_id': self.id,
            'datas': base64.encodebytes(temp.read()),
        })
        temp.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('website_blog_app.download_manifest_wizard').id,
            'res_id': attachment_id.id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }


class PrdFunction(models.Model):
    _inherit = 'prd.function'

    models_filename = fields.Char(string="Models")
    models = fields.Text(string="Models")
    data_filename = fields.Char(string="Data")
    controller_filename = fields.Char(string="Controller")
    controller = fields.Text(string="Controller")
    data = fields.Text(string="Data")
    security = fields.Text(string="Security")
    security_filename = fields.Char(string="Security XML")
    security_xml = fields.Text(string="Security XML")
    views_filename = fields.Char(string="Views")
    views = fields.Text(string="Views")
        
class OdooBranches(models.Model):
    _name = 'prd.odoo_branches'
    _description = 'Odoo Branches'

    name = fields.Char(string='View Type Name', required=True)
    active = fields.Boolean(string='Active', default=True)

class OdooProject(models.Model):
    _name = 'prd.odoo_project'
    _description = 'Odoo Project'

    # requirement.txt / requirement.repo

    name = fields.Char(string='View Type Name', required=True)
    url = fields.Char(string='View Type Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class OdooLicence(models.Model):
    _name = 'prd.odoo_lincence'
    _description = 'Odoo Branches'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Licence Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class OdooModule(models.Model):
    _name = 'prd.odoo_module'
    _description = 'Odoo Module'

    # depends in __manifest__
    # requirement.repo
    
    name = fields.Char(string='Name', required=True)
    repo_id = fields.Many2one(comodel_name='prd.odoo_repo',string="Repo",help="")
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class OdooRepo(models.Model):
    _name = 'prd.odoo_repo'
    _description = 'Odoo Repo'

    # depends in __manifest__
    # requirement.repo
    
    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='Url', help="git@github.com:vertelab/odoo-contract.git")
    path = fields.Char(string='Url', help="/usr/share/odoo-contract",)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class OdooLibrary(models.Model):
    _name = 'prd.odoo_library'
    _description = 'Odoo Library'

    # requitement.txt

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Licence Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
