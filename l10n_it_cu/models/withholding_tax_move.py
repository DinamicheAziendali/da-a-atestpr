# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class WithholdingTaxMove(models.Model):
    _inherit = 'withholding.tax.move'

    def get_se_certification_vals(self, vals):
        self.ensure_one()
        invoice = self.credit_debit_line_id.move_id
        invoice_wt_lines = invoice.withholding_tax_line_ids.filtered(
            lambda r: r.withholding_tax_id == self.withholding_tax_id
        )
        vals.update({
            'withholding_tax_id': self.withholding_tax_id.id,
            'amount_withholding_tax_deposit': self.amount,  # 9. WT deposit
        })
        # 8. WT base
        wt_invoice_amount_total_base = sum(
            invoice_wt_lines.mapped('base')) * self.withholding_tax_id.base
        wt_invoice_amount_total_tax = sum(invoice_wt_lines.mapped('tax'))
        # Proportional values using WT statement
        if self.statement_id and self.statement_id.tax:
            wt_amount_base = (
                self.amount / self.statement_id.tax
                ) * self.statement_id.base
        # Proportional values using invoices
        elif wt_invoice_amount_total_tax:
            wt_amount_base = (
                wt_invoice_amount_total_base / wt_invoice_amount_total_tax
                ) * self.amount
        else:
            wt_amount_base = wt_invoice_amount_total_tax
        vals['amount_untaxed'] = wt_amount_base
        return vals
