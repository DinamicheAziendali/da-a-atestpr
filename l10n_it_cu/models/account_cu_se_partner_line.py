# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class AccountCuSePartnerLine(models.Model):
    _name = 'account.cu.se.partner.line'
    _description = 'Account CU - Self-Employment certification - Partner Line'

    account_move_ids = fields.Many2many(
        'account.move',
        relation='account_cu_se_partner_line_account_move_rel',
        column1='account_cu_se_partner_line_id',
        column2='account_move_id',
        string="Account Moves"
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

    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        relation='account_cu_se_partner_line_account_invoice_rel',
        column1='account_cu_se_partner_line_id',
        column2='account_invoice_id',
        compute='compute_invoice_ids',
        store=True,
        string="Invoices"
    )

    se_partner_id = fields.Many2one(
        comodel_name='account.cu.se.partner',
        ondelete='cascade',
        readonly=True,
        required=True,
        string="SE Partner"
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        realted="se_partner_id.company_id",
        string="Company"
    )

    # Field are not sorted alphabetically, due to string value

    income_type_code = fields.Char(
        string="1. Income Type Reason"
    )

    year = fields.Integer(
        string="2. Year"
    )

    anticipation = fields.Boolean(
        string="3. Anticipation"
    )

    amount_total = fields.Float(
        string="4. Amount Total"
    )

    amount_ns_withholding_tax_agreement = fields.Float(
        string="5. Amount NS Withholding tax - Agreement"
    )

    code = fields.Char(
        string="6. Code"
    )

    amount_ns_withholding_tax_other = fields.Float(
        string="7. Amount NS Withholding tax - Other"
    )

    amount_untaxed = fields.Float(
        string="8. Amount Untaxed"
    )

    amount_withholding_tax_deposit = fields.Float(
        string="9. Amount Withholding Tax - Deposit"
    )

    amount_withholding_tax = fields.Float(
        string="10. Amount Withholding Tax"
    )

    amount_withholding_tax_suspended = fields.Float(
        string="11. Amount Withholding Tax - Suspended"
    )

    amount_withholding_regional_deposit = fields.Float(
        string="12. Amount Withholding Regional - Deposit"
    )

    amount_withholding_regional = fields.Float(
        string="13. Amount Withholding Regional"
    )

    amount_withholding_regional_suspended = fields.Float(
        string="14. Amount Withholding Regional - Suspended"
    )

    amount_withholding_municipal_deposit = fields.Float(
        string="15. Amount Withholding Municipal - Deposit"
    )

    amount_withholding_municipal = fields.Float(
        string="16. Amount Withholding Municipal"
    )

    amount_withholding_municipal_suspended = fields.Float(
        string="17. Amount Withholding Regional - Municipal"
    )

    amount_untaxed_previous_years = fields.Float(
        string="18. Amount Untaxed Previous Years"
    )

    amount_withholding_previous_years = fields.Float(
        string="19. Amount Withholding Previous Years"
    )

    amount_expenses_refunded = fields.Float(
        string="20. Amount Expenses Refunded"
    )

    amount_withholding_refunded = fields.Float(
        string="21. Amount Withholding Refunded"
    )

    is_social_security_required = fields.Boolean(
        compute="_compute_is_social_security_required",
        string="Social security required"
    )

    social_security_office_fiscalcode = fields.Char(
        string="29. Social Security Office Fiscal Code"
    )

    social_security_office_name = fields.Char(
        string="30. Social Security Office Name"
    )

    company_code = fields.Char(
        string="32. Company Code"
    )

    category_id = fields.Many2one(
        "account.cu.se.partner.line.category",
        string="33. Category"
    )

    employer_contributions_social_security_payments = fields.Float(
        string="34. Employer Contributions Social Security Payments"
    )

    partner_contributions_social_security_payments = fields.Float(
        string="35. Partner Contributions Social Security Payments"
    )

    other_contributions = fields.Boolean(
        string="36. Other Contributions"
    )

    other_contributions_amount = fields.Float(
        string="37. Other Contributions Amount"
    )

    contributions_due = fields.Float(
        string="38. Contributions Due"
    )

    contributions_paid = fields.Float(
        string="39. Contributions Paid"
    )

    @api.depends(
        "category_id",
        "company_code",
        "contributions_due",
        "contributions_paid",
        "employer_contributions_social_security_payments",
        "other_contributions",
        "other_contributions_amount",
        "partner_contributions_social_security_payments",
        "social_security_office_name",
    )
    def _compute_is_social_security_required(self):
        for record in self:
            record.is_social_security_required = any([
                record.social_security_office_name,
                record.company_code,
                record.category_id,
                record.employer_contributions_social_security_payments,
                record.partner_contributions_social_security_payments,
                record.other_contributions,
                record.other_contributions_amount,
                record.contributions_due,
                record.contributions_paid
            ])

    @api.depends(
        'amount_ns_withholding_tax_other',
        'code',
        'income_type_code',
    )
    def compute_error(self):
        for pl in self:
            error = False
            error_msg = ''
            if not pl.income_type_code:
                error = True
                error_msg = _('Missing Income type')
            if not pl.code and pl.amount_ns_withholding_tax_other:
                error = True
                error_msg = _(
                    'Code required for amount ns withholding tax other'
                )
            pl.update({
                'error': error,
                'error_msg': error_msg,
            })

    @api.depends(
        'account_move_ids',
        'account_move_ids.line_ids',
        'account_move_ids.line_ids.move_id',
    )
    def compute_invoice_ids(self):
        for rec in self:
            invoices = rec.account_move_ids.mapped('line_ids.move_id')
            rec.invoice_ids = [(6, 0, invoices.ids)]

    def get_line_vals(self, move_group):
        """
        To extend partner lines, use this methods
        """
        vals = {
            'account_move_ids': move_group.get('account_move_ids'),
            'amount_ns_withholding_tax_other':
                move_group.get('amount_ns_withholding_tax_other'),
            'amount_total': move_group.get('amount_total'),
            'amount_untaxed': move_group.get('amount_untaxed'),
            'amount_withholding_tax_deposit':
                move_group.get('amount_withholding_tax_deposit'),
            'income_type_code': move_group.get('income_type_code'),
            'se_partner_id': move_group.get('se_partner_id'),
        }
        return vals
