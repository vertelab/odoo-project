# -*- coding: utf-8 -*-
"""Tester för kostnadskontext på sessioner (session-cost-context).

Körs med: odoo --test-enable -u project_ai (eller checkmodule -t).
"""

from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestCostContext(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({'name': 'Kund A'})
        cls.partner_b = cls.env['res.partner'].create({'name': 'Kund B'})
        cls.project = cls.env['project.project'].create({
            'name': 'Projekt X',
            'partner_id': cls.partner_a.id,
        })
        cls.task = cls.env['project.task'].create({
            'name': 'Uppgift 1',
            'project_id': cls.project.id,
        })
        cls.coworker = cls.env['ai.coworker'].create({
            'name': 'Test Kostnad',
            'status': 'active',
            'cost_context_question': 'Vilket projekt gäller detta arbete?',
            'cost_context_partner_strategy': 'project_partner',
        })

    def _session(self, **kw):
        return self.env['ai.coworker.session'].create(
            dict({'coworker_id': self.coworker.id, 'status': 'active'}, **kw))

    def test_task_capture_sets_context(self):
        """9.1: taggning via _capture_session_from_task → task/projekt/partner."""
        sess = self._session()
        with self.env.context(_ai_context_model='ai.coworker.session',
                              _ai_context_id=sess.id):
            self.env['ai.coworker']._capture_session_from_task(self.task.id)
        self.assertEqual(sess.task_id, self.task)
        self.assertEqual(sess.project_id, self.project)
        self.assertEqual(sess.partner_id, self.partner_a)  # task→projekt→partner

    def test_project_only_derives_partner(self):
        """9.2: enbart projekt → partner via strategi; utan kontext → tomma."""
        sess = self._session(project_id=self.project.id)
        sess._session_capture_context()
        self.assertEqual(sess.partner_id, self.partner_a)

        empty = self._session()
        empty._session_capture_context()
        self.assertFalse(empty.project_id)
        self.assertFalse(empty.task_id)
        self.assertFalse(empty.partner_id)

    def test_lookup_lifecycle(self):
        """9.3: nytt UUID skapar; befintligt återfinner; copy_from kopierar."""
        Session = self.env['ai.coworker.session']
        s1, created = Session._lookup_or_create_pi_session('uuid-1')
        self.assertTrue(created)
        s1._capture_context(task=self.task)
        s1.write({'cost_context_confirmed': True})

        s2, created2 = Session._lookup_or_create_pi_session('uuid-1')
        self.assertFalse(created2)
        self.assertEqual(s2.id, s1.id)
        self.assertEqual(s2.partner_id, self.partner_a)
        self.assertTrue(s2.cost_context_confirmed)

        # Fork: nytt UUID + copy_from → ny session med kopierad kontext
        s3, created3 = Session._lookup_or_create_pi_session(
            'uuid-2', copy_from_pi_session_id='uuid-1')
        self.assertTrue(created3)
        self.assertNotEqual(s3.id, s1.id)
        self.assertEqual(s3.project_id, self.project)
        self.assertEqual(s3.task_id, self.task)
        self.assertEqual(s3.partner_id, self.partner_a)
        self.assertTrue(s3.cost_context_confirmed)

    def test_cost_context_set_semantics(self):
        """9.4: cost_context_set skriver + bekräftar (modellnivå)."""
        sess = self._session()
        sess._capture_context(project=self.project)
        sess._apply_cost_context_strategy()
        self.assertEqual(sess.partner_id, self.partner_a)
        sess.write({'cost_context_confirmed': True})
        self.assertTrue(sess.cost_context_confirmed)
        self.assertEqual(sess.coworker_id.cost_context_partner_strategy,
                         'project_partner')

    def test_reused_session_last_context_wins(self):
        """9.5: återanvändbar session — ny task uppdaterar, lines orörda."""
        project2 = self.env['project.project'].create({
            'name': 'Projekt Y',
            'partner_id': self.partner_b.id,
        })
        task2 = self.env['project.task'].create({
            'name': 'Uppgift 2',
            'project_id': project2.id,
        })
        sess = self._session()
        sess._capture_context(task=self.task)
        self.assertEqual(sess.partner_id, self.partner_a)
        lines_before = len(sess.session_line_ids)
        sess._capture_context(task=task2)
        self.assertEqual(sess.task_id, task2)
        self.assertEqual(sess.project_id, project2)
        self.assertEqual(sess.partner_id, self.partner_b)
        self.assertEqual(len(sess.session_line_ids), lines_before)

    def test_smart_buttons_and_aggregation(self):
        """9.6: computed-fält på projekt/partner + token-aggregering."""
        s1 = self._session(project_id=self.project.id,
                           partner_id=self.partner_a.id)
        s1.write({'token_input': 100, 'token_output': 50})
        s2 = self._session(project_id=self.project.id,
                           partner_id=self.partner_a.id)
        s2.write({'token_input': 30, 'token_output': 20})
        self.assertEqual(self.project.ai_session_count, 2)
        self.assertEqual(self.project.ai_token_total, 200)
        self.assertEqual(self.partner_a.ai_session_count, 2)
        self.assertEqual(self.partner_a.ai_token_total, 200)
        self.assertEqual(self.partner_b.ai_session_count, 0)
        self.assertEqual(self.partner_b.ai_token_total, 0)
