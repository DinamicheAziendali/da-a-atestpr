# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountCuSePartner(models.Model):
    _name = 'account.cu.se.partner'
    _description = 'Account CU - Self-Employment certification - Partner'

    amount_total = fields.Float(
        compute='compute_amounts',
        store=True,
        string="4. Amount Total"
    )

    amount_ns_withholding_tax_other = fields.Float(
        compute='compute_amounts',
        store=True,
        string="7. Amount NS Withholding tax - Other"
    )

    amount_untaxed = fields.Float(
        compute='compute_amounts',
        store=True,
        string="8. Amount Untaxed"
    )

    amount_withholding_tax_deposit = fields.Float(
        string="9. Amount Withholding Tax - Deposit"
    )

    birth_date = fields.Date(
        string="Birth Date",
    )

    birth_city = fields.Char(
        string="Birth City/Strange Country",
    )

    birth_province = fields.Char(
        string="Birth Province",
    )

    confirmed = fields.Boolean(
        help="If confirmed, this partner won't be recomputed",
        string="Confirmed",
    )

    exceptional_events = fields.Char(
        string="Exceptional events"
    )

    domicile_1_city = fields.Char(
        string="City of first domicile",
    )

    domicile_1_city_code = fields.Char(
        string="City Code",
    )

    domicile_1_city_merge_code = fields.Char(
        string="City Merge Code first domicile",
    )

    domicile_1_province = fields.Char(
        string="Province first domicile",
    )

    domicile_2_city = fields.Char(
        string="City second domicile",
    )

    domicile_2_city_code = fields.Char(
        string="City Code",
    )

    domicile_2_city_merge_code = fields.Char(
        string="City Merge Code City second domicile",
    )

    domicile_2_province = fields.Char(
        string="Province second domicile",
    )

    exclusion_cases = fields.Char(
        string="Exclusion Cases",
    )

    error = fields.Boolean(
        compute="compute_error",
        store=True,
        string="Error"
    )

    error_msg = fields.Char(
        compute="compute_error",
        store=True,
        string="Error Description"
    )

    firstname = fields.Char(
        string="First name",
    )

    fiscalcode = fields.Char(
        string="Fiscalcode"
    )

    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other")
        ]
    )

    lastname = fields.Char(
        string="Last name / Company Name",
    )

    line_ids = fields.One2many(
        comodel_name='account.cu.se.partner.line',
        inverse_name='se_partner_id',
        string="SE Partner lines"
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner"
    )

    special_categories = fields.Char(
        string="Special Categories"
    )

    statement_id = fields.Many2one(
        comodel_name='account.cu.statement',
        ondelete='cascade',
        readonly=True,
        required=True,
        string="CU Statement"
    )

    statement_type_id = fields.Many2one(
        comodel_name='account.cu.statement.type',
        related='statement_id.statement_type_id',
        store=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        related="statement_id.company_id",
        string="Company"
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("done", "Done"),
        ("error", "Error"),
        ("cancelled", "Cancelled"),
        ("substitution", "Substitution"),
    ], default="draft", string="State")

    ade_protocol = fields.Char(
        string="ADE Protocol",
        copy=False,
    )

    ade_sequence = fields.Char(
        string="ADE Sequence",
        copy=False,
    )

    ade_operation = fields.Selection(
        selection=[
            ("A", "Cancelled"),
            ("S", "Substitution")
        ],
        copy=False,
        string="ADE Operation",
    )

    record_dh_txt = fields.Text(
        string="RecordDH Text",
        copy=False,
    )

    @api.depends(
        'line_ids',
        'line_ids.amount_total',
        'line_ids.amount_ns_withholding_tax_other',
        'line_ids.amount_untaxed',
        'line_ids.amount_withholding_tax_deposit',
    )
    def compute_amounts(self):
        for rec in self:
            rec_lines = rec.line_ids
            rec.update({
                'amount_total': sum(rec_lines.mapped('amount_total')),
                'amount_ns_withholding_tax_other': sum(
                    rec_lines.mapped('amount_ns_withholding_tax_other')
                ),
                'amount_untaxed': sum(
                    rec_lines.mapped('amount_untaxed')
                ),
                'amount_withholding_tax_deposit': sum(
                    rec_lines.mapped('amount_withholding_tax_deposit')
                ),
            })

    def set_done(self):
        for rec in self:
            rec.state = "done"

    def set_cancelled(self):
        for rec in self:
            if rec.ade_protocol and rec.ade_sequence and rec.ade_operation:
                rec.state = "cancelled"
            else:
                raise UserError(_(
                    "You must set these fields before set 'Cancelled': "
                    "ADE Protocol, ADE Sequence, ADE Operation"
                ))

    def set_substitution(self):
        for rec in self:
            if rec.ade_protocol and rec.ade_sequence and rec.ade_operation:
                rec.state = "substitution"
            else:
                raise UserError(_(
                    "You must set these fields before set 'Substitution': "
                    "ADE Protocol, ADE Sequence, ADE Operation"
                ))

    def reset_to_draft(self):
        for rec in self:
            rec.state = "draft"

    @api.depends(
        'line_ids',
        'line_ids.error',
        'line_ids.error_msg',
    )
    def compute_error(self):
        for rec in self:
            error = bool(rec.line_ids.filtered('error'))
            error_msg = ', '.join(
                set(rec.line_ids.filtered('error_msg').mapped('error_msg')))

            rec.error = error
            rec.error_msg = error_msg
            if error:
                rec.state = "error"

    def get_line_vals(self, wt_move_group):
        vals = {
            'se_partner_id': self.id,
            'income_type_code': wt_move_group.get('payment_reason').code
        }
        return vals

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            partner = self.partner_id
            self.update({
                'fiscalcode': partner.fiscalcode,
                'firstname': partner.firstname,
                'lastname': partner.lastname,
                'gender': partner.gender,
                'birth_date': partner.birthdate_date,
                'birth_city': partner.birth_city,
                'birth_province': partner.birth_state_id.code or '',
            })
