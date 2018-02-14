# -*- coding: utf-8 -*-
# © 2015 Jordi Riera <kender.jr@gmail.com>
# © 2017-2018 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import models, api, _
from odoo.exceptions import ValidationError

try:
    import phonenumbers
except ImportError:
    raise ImportError()

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_warning(self, msg, is_constrain=None):
        """Raise warning or exceptions based on policy"""
        policy = self.env['ir.config_parameter'].sudo().get_param(
            'base_phone_validation.policy')
        if policy == 'soft':
            return {'warning': {'title': _('Warning'), 'message': msg}}
        elif policy == 'strict' and is_constrain:
            raise ValidationError(msg)

    def _force_validation(self, phonenumber, fieldname, is_constrain=None):
        """Force the validation using phonenumbers of a given number

        :param phonenumber: string
        :param str fieldname: name of the field the number is related to.
        :raise ValidationError: if the given number is not validated.
        """
        if self.country_id:
            number = phonenumbers.parse(phonenumber, self.country_id.code)
            if not phonenumbers.is_valid_number_for_region(
                    number, self.country_id.code):
                error_msg = u'\n'.join([
                    _(u'The number ({}) "{}" seems not valid for {}.').format(
                        fieldname, phonenumber, self.country_id.name
                    ),
                    _(u'Please double check it.')
                ])
                return self._get_warning(error_msg, is_constrain)

        elif self.env.user.company_id.country_id:
            local_country = self.env.user.company_id.country_id
            number = phonenumbers.parse(
                phonenumber, local_country.code)
            if not phonenumbers.is_valid_number_for_region(
                    number, local_country.code):
                error_msg = u'\n'.join([
                    _(u'The number ({}) "{}" seems not valid for {}.').format(
                        fieldname, phonenumber, local_country.name
                    ),
                    _(u'Please double check it.')
                ])
                return self._get_warning(error_msg, is_constrain)

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone:
            return self._force_validation(self.phone, 'phone')

    @api.constrains('phone', 'country_id')
    def _phone_number_validation(self):
        for rec in self:
            if rec.phone:
                rec._force_validation(rec.phone, 'phone', True)

    @api.onchange('fax')
    def _onchange_fax(self):
        if self.fax:
            return self._force_validation(self.fax, 'fax')

    @api.constrains('fax', 'country_id')
    def _fax_number_validation(self):
        for rec in self:
            if rec.fax:
                rec._force_validation(rec.fax, 'fax', True)

    @api.onchange('mobile')
    def _onchange_mobile(self):
        if self.mobile:
            return self._force_validation(self.mobile, 'mobile')

    @api.constrains('mobile', 'country_id')
    def _mobile_number_validation(self):
        for rec in self:
            if rec.mobile:
                rec._force_validation(rec.mobile, 'mobile', True)
