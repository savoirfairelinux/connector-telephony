# -*- coding: utf-8 -*-
# © 2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class CRMSettings(models.TransientModel):

    _name = 'sale.config.settings'
    _inherit = ['sale.config.settings']

    phone_number_policy = fields.Selection(
        [('soft', 'Soft'), ('strict', 'Strict')],
        help='Soft only warn the user / Strict raise an error',
    )

    @api.model
    def get_default_policy(self, fields):
        policy = self.env['ir.config_parameter'].sudo(
        ).get_param('base_phone_validation.policy')
        return {'phone_number_policy': policy}

    @api.multi
    def set_policy(self):
        for rec in self:
            self.env['ir.config_parameter'].set_param(
                'base_phone_validation.policy',
                rec.phone_number_policy or ''
            )
