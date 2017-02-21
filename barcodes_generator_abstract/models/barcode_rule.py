# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _, exceptions

_GENERATE_TYPE = [
    ('no', 'No generation'),
    ('manual', 'Base set Manually'),
    ('sequence', 'Base managed by Sequence'),
]


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    # Column Section
    generate_type = fields.Selection(
        string='Generate Type', selection=_GENERATE_TYPE,
        required=True, default='no',
        help="Allow to generate barcode, including a number"
        "  (a base) in the final barcode.\n"
        " 'Base Set Manually' : User should set manually the value of the"
        " barcode base\n"
        " 'Base managed by Sequence': User will use a button to generate a"
        " new base. This base will be generated by a sequence")

    generate_model = fields.Selection(
        string='Generate Model', selection=[],
        help="if 'Generate Type' is set, mention the model related to this"
        " rule.")

    padding = fields.Integer(
        string='Padding', compute='_compute_padding', readonly=True,
        store=True)

    sequence_id = fields.Many2one(
        string='Sequence', comodel_name='ir.sequence')

    # Compute Section
    @api.depends('pattern')
    @api.multi
    def _compute_padding(self):
        for rule in self:
            rule.padding = rule.pattern.count('.')

    # On Change Section
    @api.onchange('generate_type')
    @api.multi
    def onchange_generate_type(self):
        for rule in self:
            if rule.generate_type == 'no':
                rule.generate_model = False

    # View Section
    @api.multi
    def generate_sequence(self):
        sequence_obj = self.env['ir.sequence']
        for rule in self:
            if rule.generate_type != 'sequence':
                raise exceptions.UserError(_(
                    "Generate Sequence is possible only if  'Generate Type'"
                    " is set to 'Base managed by Sequence'"))
            sequence = sequence_obj.create(self._prepare_sequence(rule))
            rule.sequence_id = sequence.id

    # Custom Section
    @api.model
    def _prepare_sequence(self, rule):
        return {
            'name': _('Sequence - %s') % rule.name,
            'padding': rule.padding,
        }
