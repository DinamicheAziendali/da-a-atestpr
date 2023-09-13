# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountCuSePartnerLineCategory(models.Model):
    _name = "account.cu.se.partner.line.category"
    _description = "Account CU - Self-Employment certification\
        - Partner Line - Category"

    name = fields.Char(
        string="Name"
    )
