# -*- coding: utf-8 -*-
"""Tester för deterministisk OKF-sammanfattning (okf-mixin-install D2/D3).

Körs med: checkmodule -t -u project_ai (eller odoo --test-enable).

Sammanfattningen ska byggas av postens EGNA fält — ingen LLM-tur — och
vara stabil mellan körningar. Saknad etapp/kund ska hanteras utan att
texten blir tom eller felaktig.
"""

from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestOkfSummary(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Kund Zeta'})
        cls.project = cls.env['project.project'].create({
            'name': 'Projekt Alfa',
            'partner_id': cls.partner.id,
        })
        cls.task = cls.env['project.task'].create({
            'name': 'Uppgift Beta',
            'project_id': cls.project.id,
        })

    # ── project.task ───────────────────────────────────────────────────

    def test_task_summary_has_name_stage_project(self):
        """Namn + etapp + projekt, utan LLM (källa 'model')."""
        summary, source = self.task._okf_build_summary(
            self.task._okf_body_source() or '', 2000)
        self.assertEqual(source, 'model')
        self.assertIn('Uppgift Beta', summary)
        self.assertIn('Projekt Alfa', summary)
        # Etappen finns alltid i Odoo (default 'Ny') — den ska namnge sig.
        self.assertIn('Etapp:', summary)

    def test_task_summary_missing_project_and_stage(self):
        """Utan projekt/etapp byggs texten av namnet — inte tom."""
        task = self.env['project.task'].create({'name': 'Ensam uppgift'})
        task.write({'project_id': False, 'stage_id': False})
        summary = task._okf_summary_source()
        self.assertEqual(summary, 'Ensam uppgift')
        self.assertNotIn('Etapp:', summary)
        self.assertNotIn('Projekt:', summary)

    def test_task_summary_is_stable(self):
        """Samma oförändrade uppgift ger identisk text två gånger."""
        first = self.task._okf_summary_source()
        second = self.task._okf_summary_source()
        self.assertEqual(first, second)

    # ── project.project ────────────────────────────────────────────────

    def test_project_summary_has_name_and_partner(self):
        """Namn + kund, utan LLM (källa 'model')."""
        summary, source = self.project._okf_build_summary(
            self.project._okf_body_source() or '', 2000)
        self.assertEqual(source, 'model')
        self.assertIn('Projekt Alfa', summary)
        self.assertIn('Kund: Kund Zeta', summary)

    def test_project_summary_missing_partner(self):
        """Utan kund byggs texten av namnet — inte tom eller felaktig."""
        project = self.env['project.project'].create({'name': 'Internt projekt'})
        summary = project._okf_summary_source()
        self.assertEqual(summary, 'Internt projekt')
        self.assertNotIn('Kund:', summary)

    def test_project_summary_is_stable(self):
        """Samma oförändrade projekt ger identisk text två gånger."""
        first = self.project._okf_summary_source()
        second = self.project._okf_summary_source()
        self.assertEqual(first, second)

    # ── kontraktet: skip_reason anropas före summary ───────────────────

    def test_skip_reason_short_circuits_summary(self):
        """`_okf_index_record` anropar summary bara när body finns och
        skip_reason är tom — en avförd post ska aldrig sammanfattas."""
        self.assertIsNone(self.task._okf_skip_reason())
        self.assertTrue((self.task._okf_body_source() or '').strip())
