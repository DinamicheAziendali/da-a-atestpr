# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    income_type_id = fields.Many2one(
        comodel_name='payment.reason',
        string="Income Type"
    )
