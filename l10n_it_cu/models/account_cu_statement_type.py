# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountCuStatementType(models.Model):
    _name = 'account.cu.statement.type'
    _description = 'CU Statements Type'

    certification_se_method_compute = fields.Char(
        string="Method to use for compute values"
    )

    certification_se_method_print = fields.Char(
        string="Method to use for print values"
    )

    certification_se_method_export = fields.Char(
        string="Method to use for export values"
    )

    date_start = fields.Date(
        string="Start Date"
    )

    date_stop = fields.Date(
        string="Stop Date"
    )

    name = fields.Char(
        required=True,
        string="Name"
    )

    supply_code = fields.Char(
        required=True,
        string="Supply Code"
    )

    income_year = fields.Integer(
        required=True,
        string="Income Year"
    )
