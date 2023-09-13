# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools import float_round


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cu_payment_subject = fields.Boolean(
        compute='_compute_amount_residual',
        store=True,
        string="Payment subject to CU"
    )

    # Forse invece che estendere il metodo, conviene farne uno specifico per
    # questo caso d'uso?
    # def _compute_amount_residual(self):
    #     res = super()._compute_amount_residual()
    #     for line in self:
    #         line.cu_payment_subject = line._get_cu_payment()
    #     return res

    def _get_cu_payment(self):
        self.ensure_one()
        if self.account_internal_type != 'payable':
            return False
        # Righe collegate
        if self.debit:
            rec_amls = self.matched_credit_ids.mapped('credit_move_id')
        else:
            rec_amls = self.matched_debit_ids.mapped('debit_move_id')

        amls_subj_to_wt = rec_amls.filtered(
            lambda aml: aml.move_id.line_ids.invoice_line_tax_wt_ids
        )

        am_subj_to_wt = rec_amls.filtered(
            lambda aml:  aml.move_id.fiscal_position_id.income_type_id or
            aml.move_id.fiscal_position_id.withholding_tax_ids
        )

        partner_subj_to_wt = rec_amls.filtered(
            lambda aml: aml.move_id.partner_id.income_type_id or
            aml.move_id.partner_id.property_account_position_id.withholding_tax_ids or
            aml.move_id.partner_id.property_account_position_id.income_type_id
        )

        return any([
            amls_subj_to_wt,
            am_subj_to_wt,
            partner_subj_to_wt
        ])

    def get_se_certification_vals(self):
        self.ensure_one()
        vals = {}
        wt_move_obj = self.env['withholding.tax.move']
        amount_dp = self.env['decimal.precision'].precision_get('Account')
        # Invoices competence through reconciles
        ams = self.get_invoices_from_reconcile()

        vals.update({
            'account_move_ids': ams.ids,
            'partner_id': self.partner_id.id,
            'invoices': ams,
        })

        # Vals from WT Move
        domain = [
            ('payment_line_id', '=', self.id),
            ('withholding_tax_id.wt_types', '=', 'ritenuta'),
            ('company_id', '=', self.company_id.id)
        ]
        wt_moves = wt_move_obj.search(domain)

        if wt_moves:
            amount_untaxed = 0
            amount_withholding_tax_deposit = 0
            for wt_move in wt_moves:
                wt_vals = wt_move.get_se_certification_vals(vals)
                amount_untaxed += wt_vals.get('amount_untaxed', 0)
                amount_withholding_tax_deposit += wt_vals.get(
                    'amount_withholding_tax_deposit',
                    0
                )
            vals.update({
                'amount_untaxed': float_round(amount_untaxed, amount_dp),
                'amount_withholding_tax_deposit': float_round(
                    amount_withholding_tax_deposit,
                    amount_dp
                ),
            })
        # Income type
        income_type_id = self.get_income_type_id(wt_moves, ams)
        vals['income_type_code'] = income_type_id.code or ''
        return vals

    def get_income_type_id(self, wt_moves, invoices):
        """
        It returns income type using the following priority:
        - 1. Payment reason from WT
        - 2. Income type from invoice's fiscal position
        - 3. Income type from partner
        """
        self.ensure_one()
        partner = self.partner_id
        fp = invoices.mapped(
            'fiscal_position_id'
        ).filtered(
            'income_type_id'
        )[:1]
        if wt_moves and wt_moves.mapped(
            'withholding_tax_id.payment_reason_id'
        ):
            income_type_id = wt_moves.mapped(
                'withholding_tax_id.payment_reason_id'
            )[:1]
        elif fp and fp.income_type_id:
            income_type_id = fp.income_type_id
        else:
            income_type_id = partner.income_type_id
        return income_type_id

    def get_invoices_from_reconcile(self):
        """
        It will take all AMLS reconciled with payment line,
        filtering only AMS of document subject to CU
        Returns:
            AMS: recorset of account moves
        """
        self.ensure_one()
        ams = self.matched_credit_ids.mapped(
            'debit_move_id.move_id')
        ams |= self.matched_credit_ids.mapped(
            'credit_move_id.move_id')
        ams |= self.matched_debit_ids.mapped(
            'debit_move_id.move_id')
        ams |= self.matched_debit_ids.mapped(
            'credit_move_id.move_id')

        ams = ams.filtered(lambda r: r.move_type == 'in_invoice')
        return ams
