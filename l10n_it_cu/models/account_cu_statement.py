# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus.paragraph import Paragraph

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class AccountCuStatement(models.Model):
    _name = 'account.cu.statement'
    _description = 'CU Statements'
    _inherit = ['mail.thread']

    def _default_company(self):
        company_id = self._context.get('company_id', self.env.company.id)
        return company_id

    def _default_employer(self):
        return self.env.company.partner_id

    def _default_statement_type(self):
        """
        Take the most recent Statement type available
        """
        return self.env['account.cu.statement.type'].search(
            [],
            order='id desc',
            limit=1
        )

    certification_count = fields.Integer(
        compute="_compute_certification_count",
        string="Certification Count"
    )

    certification_se = fields.Boolean(
        string="Self-Employment certification, commissions and different\
        incomes"
    )

    certification_se_lines_ids = fields.One2many(
        comodel_name='account.cu.se.partner',
        inverse_name='statement_id',
        string="SE Lines"
    )

    certification_se_method_compute = fields.Char(
        related='statement_type_id.certification_se_method_compute',
        string="Method to use for compute values"
    )

    certification_se_method_print = fields.Char(
        related='statement_type_id.certification_se_method_print',
        string="Method to use for print values"
    )

    certification_se_method_export = fields.Char(
        related='statement_type_id.certification_se_method_export',
        string="Method to use for export values"
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=_default_company,
        string="Company"
    )

    date_start = fields.Date(
        string="Start Date"
    )

    date_stop = fields.Date(
        string="Stop Date"
    )

    delegate_sign = fields.Char(
        string="Delegate Sign",
    )

    delegate_fiscalcode = fields.Char(
        string="Delegate Fiscalcode",
    )

    delegate_date = fields.Date(
        string="Delegate Date",
    )

    delegate_commitment = fields.Char(
        string="Commitment to submit statement electronically",
        required=True,
    )

    employer_address = fields.Char(
        string="Address",
    )

    employer_ateco_id = fields.Many2one(
        comodel_name='ateco.category',
        string="Ateco Code",
    )

    employer_city = fields.Char(
        string="City"
    )

    employer_email = fields.Char(
        string="Email",
    )

    employer_firstname = fields.Char(
        string="First name"
    )

    employer_fiscalcode = fields.Char(
        string="Fiscalcode"
    )

    employer_headquarters = fields.Char(
        string="Headquarters Code"
    )

    employer_id = fields.Many2one(
        comodel_name='res.partner',
        default=_default_employer,
        required=True,
        string="Employer / Withholding Agent"
    )

    employer_lastname = fields.Char(
        string="Last name"
    )

    employer_phone = fields.Char(
        string="Phone",
    )

    employer_province = fields.Char(
        string="Province",
    )

    employer_zip = fields.Char(
        string="Zip",
    )

    name = fields.Char(
        related='statement_type_id.name',
        store=True,
        string="Name"
    )

    statement_date = fields.Date(
        default=fields.Date.today(),
        required=True,
        string="Date"
    )

    statement_sign = fields.Char(
        string="Statement Sign",
    )

    statement_type_id = fields.Many2one(
        comodel_name='account.cu.statement.type',
        default=_default_statement_type,
        required=True,
        string="Statement Type"
    )

    taxpayer_appointment_code_id = fields.Many2one(
        comodel_name="appointment.code",
        string="Taxpayer Appointment Code",
    )

    taxpayer_firstname = fields.Char(
        string="Taxpayer Firstname",
    )

    taxpayer_fiscalcode = fields.Char(
        string="Taxpayer Fiscalcode",
    )

    taxpayer_lastname = fields.Char(
        string="Taxpayer Lastname",
    )

    taxpayer_sign = fields.Char(
        required=True,
        string="Taxpayer Sign"
    )

    record_ab_txt = fields.Text(
        string="RecordAB Text",
        copy=False,
    )

    #
    # OnChange methods
    #

    @api.onchange('statement_type_id')
    def onchange_statement_type_id(self):
        if self.statement_type_id:
            statement_type = self.statement_type_id
            self.update({
                'date_start': statement_type.date_start,
                'date_stop': statement_type.date_stop,
            })

    @api.onchange('employer_id')
    def onchange_employer_id(self):
        if self.employer_id:
            employer = self.employer_id
            self.update({
                'employer_fiscalcode': employer.fiscalcode,
                'employer_firstname': employer.firstname,
                'employer_lastname': employer.lastname,
                'employer_city': employer.city,
                'employer_province': employer.state_id.code,
                'employer_zip': employer.zip,
                'employer_address': f'{employer.street} {employer.street2}',
                'employer_phone': employer.phone,
                'employer_email': employer.email,
                'employer_ateco_id': employer.ateco_category_ids[:1],
            })

    #
    # Compute methods
    #

    @api.depends("certification_se_lines_ids")
    def _compute_certification_count(self):
        for statement in self:
            statement.certification_count = len(
                statement.certification_se_lines_ids
            )

    #
    # Button methods
    #

    def button_statement_compute(self):
        """
        The methods are linked through statements type to manage possible
        changes in the coming years
        """
        # SE Certifications
        se_method_name = self.statement_type_id.certification_se_method_compute
        target = "compute SE Certification"
        self.check_method(se_method_name, target)
        getattr(type(self), se_method_name)(self)

    def button_statement_print(self):
        self.ensure_one()
        # SE Certifications
        se_method_name = self.statement_type_id.certification_se_method_print
        target = "print SE Certification"
        self.check_method(se_method_name, target)
        getattr(type(self), se_method_name)(self)

    def button_statement_export(self):
        self.ensure_one()
        # SE Certifications
        se_method_name = self.statement_type_id.certification_se_method_export
        target = "export SE Certification"
        self.check_method(se_method_name, target)
        getattr(type(self), se_method_name)(self)

    def button_statement_copy(self):
        # SE Certifications
        new_statement = self.copy()
        for se_partner in self.certification_se_lines_ids:
            new_se_partner = se_partner.copy({
                "statement_id": new_statement.id
            })
            for line in se_partner.line_ids:
                line.copy({
                    "se_partner_id": new_se_partner.id
                })

    #
    # Helper methods
    #

    def check_method(self, method_name, target):
        if not hasattr(type(self), method_name):
            raise UserError(
                _(
                    "The method '{method}' is not valid to {target}! "
                    "You can set it in Statement Type"
                ).format(
                    method=method_name,
                    target=target
                )
            )

    def check_move_group(self, move_group):
        """
        In the move_group are computed all values subjected to CU.
        If there aren't values, the partner won't be included
        in the SE lines.

        Returns:
            True/False: False if the partner must be excluded
        """
        if not move_group.get('income_type_code', False):
            return False
        else:
            return True

    #
    # Business Logic
    #

    def generate_se_certification(self):
        """
        Generate data for SE Certification
        """
        acuse_partner_obj = self.env['account.cu.se.partner']
        acuse_partner_line_obj = self.env['account.cu.se.partner.line']
        # Unlik existing lines
        self.certification_se_lines_ids.filtered(
            lambda r: not r.confirmed
        ).unlink()
        partners_confirmed_ids = self.certification_se_lines_ids.mapped(
            'partner_id'
        ).ids
        # Recompute new lines
        # Get all supplier payments
        amls = self.get_payment_lines()
        # Group payments by partner and set income type
        # of competence to determine whether it is subject or not
        # to CU
        moves_group = self.get_payment_lines_group(amls)
        se_partner_section = dict()
        se_partner_lines = acuse_partner_line_obj
        for group in moves_group:
            move_group = moves_group[group]
            # Check if partner must be included in CU
            if not self.check_move_group(move_group):
                continue
            # Partner
            partner_id = move_group.get('partner_id', False)
            if partner_id in partners_confirmed_ids:
                continue
            if partner_id not in se_partner_section:
                vals = self.get_se_partner_vals(move_group)
                acuse_partner = acuse_partner_obj.create(vals)
                se_partner_section[partner_id] = acuse_partner
                acuse_partner.onchange_partner_id()
            else:
                acuse_partner = se_partner_section[partner_id]
            # Partner Line
            move_group.update({
                'income_type_code': move_group.get('income_type_code'),
                'partner_id': partner_id,
                'statement_id': self.id,
                'se_partner_id': acuse_partner.id,
            })
            # ... Recompute total documents
            # From single payment line, it's possible to compute amount base
            # and amount of taxes. The amount total of document of competence
            # must be computed after all taxes are grouped under partner line.
            # It will set the following fields:
            # 4. Invoice total untaxed
            # 7. Other
            self.set_total_documents(move_group)
            # ... Account moves to save in rec
            if move_group.get('account_move_ids'):
                move_group.update({
                    'account_move_ids': [
                        (6, 0, move_group.get('account_move_ids'))]
                })
            # ... Hook
            vals = acuse_partner_line_obj.get_line_vals(move_group)
            acuse_partner_line = acuse_partner_line_obj.create(vals)
            se_partner_lines |= acuse_partner_line
        return se_partner_lines

    def get_payment_lines(self):
        aml_obj = self.env['account.move.line']
        domain = self.get_payment_lines_domain()
        amls = aml_obj.search(domain)
        return amls

    def get_payment_lines_domain(self):
        domain = [
            ('account_internal_type', '=', 'payable'),
            ('company_id', '>=', self.company_id.id),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_stop),
            ('parent_state', '=', 'posted'),
            ('move_id.move_type', 'in', ('entry', 'in_refund')),
        ]
        return domain

    def get_payment_lines_key(self, payment_data):
        key = (
            payment_data.get('partner_id'),
            payment_data.get('income_type_id')
        )
        return key

    def get_payment_lines_group(self, amls):
        """
        This method receives all payment in the period of CU.
        It group these payments by partner and set the income type.
        It's possibile to have group without income type. These groups
        will be excluded from CU.

        Args:
            amls: all payments of the period

        Returns:
            moves_group: dictonary with couple partner-income type and
                amounts of competence
        """
        moves_group = dict()
        # From payment lines to debit/credit lines
        for aml in amls:
            payment_data = aml.get_se_certification_vals()
            group_key = self.get_payment_lines_key(payment_data)
            if group_key not in moves_group:
                moves_group[group_key] = {
                    'income_type_code': payment_data.get('income_type_code'),
                    'income_type_id': payment_data.get('income_type_id'),
                    'partner_id': payment_data.get('partner_id'),
                    'withholding_tax_id':
                        payment_data.get('withholding_tax_id'),
                    'amount_total': 0,
                    'amount_ns_withholding_tax_other': 0,
                    'amount_untaxed': 0,
                    'amount_withholding_tax_deposit': 0,
                    'account_move_ids': [],
                }
            moves_group[group_key]['amount_total'] +=\
                payment_data.get('amount_total', 0)
            moves_group[group_key]['amount_ns_withholding_tax_other'] +=\
                payment_data.get('amount_ns_withholding_tax_other', 0)
            moves_group[group_key]['amount_untaxed'] +=\
                payment_data.get('amount_untaxed', 0)
            moves_group[group_key]['amount_withholding_tax_deposit'] +=\
                payment_data.get('amount_withholding_tax_deposit', 0)
            if payment_data.get('account_move_ids'):
                am_ids = payment_data.get('account_move_ids')
                for am_id in am_ids:
                    if am_id not in moves_group[group_key]['account_move_ids']:
                        moves_group[group_key]['account_move_ids'].append(
                            am_id)
        return moves_group

    def get_se_partner_vals(self, move_group):
        vals = {
            'statement_id': self.id,
            'partner_id': move_group.get('partner_id'),
        }
        return vals

    def get_total_document(self, account_move):
        """
        This method returns the amount document subjected to CU.
        If the document is partially paid, the total amount will be
        computed with the quote paid.

        Returns:
            amount : amount proportional to the amount paid
        """
        amount_dp = self.env['decimal.precision'].precision_get(
            'Account'
        )
        # Supplier invoice balance is negative, but in the CU
        # I need to have positive values
        lines_total = -1 * sum(
            line.balance for line in account_move.line_ids
            if line.cu_payment_subject
        )

        amount_paid = float_round(
            abs(lines_total),
            amount_dp
        )
        # Document full paid
        if float_compare(
                account_move.amount_total, amount_paid, amount_dp) == 0:
            amount = float_round(
                -1 * account_move.amount_untaxed_signed,
                amount_dp
            )
        # Document partially paid
        elif account_move.amount_total:
            amount = float_round(
                -1 * account_move.amount_untaxed_signed * (
                    amount_paid / account_move.amount_total
                ),
                amount_dp
            )
        else:
            amount = 0
        return amount

    def set_total_documents(self, move_group):
        """
        To extend partner lines, use this methods
        """
        amount_dp = self.env['decimal.precision'].precision_get('Account')
        am_obj = self.env['account.move']
        am_ids = move_group.get('account_move_ids')
        if am_ids:
            ams = am_obj.browse(am_ids)
            amount_total = sum([
                self.get_total_document(am) for am in ams
            ])
            move_group.update({
                'amount_total': float_round(amount_total, amount_dp),
                'amount_ns_withholding_tax_other': float_round(
                    amount_total - move_group.get('amount_untaxed'),
                    amount_dp
                )
            })
        return move_group

    def manage_cu_coordinate_field_many2one(self, cu_coordinate_id, model_id, report):
        if model_id.mapped(cu_coordinate_id.field_id.name):
            if cu_coordinate_id.field_id.name in [
                "employer_ateco_id", "taxpayer_appointment_code_id"
            ]:
                text = str(
                    model_id.mapped(
                        cu_coordinate_id.field_id.name
                    )[0].code
                )
            else:
                text = str(
                    model_id.mapped(
                        cu_coordinate_id.field_id.name
                    )[0].display_name
                )
        else:
            text = ""
        report.drawString(
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm,
            text
        )

    def manage_cu_coordinate_field_selection(self, cu_coordinate_id, model_id, report):
        if model_id.mapped(cu_coordinate_id.field_id.name)[0]:
            if cu_coordinate_id.field_id.name == "gender":
                if model_id.mapped(
                        cu_coordinate_id.field_id.name
                )[0] == "male":
                    text = "M"
                elif model_id.mapped(
                        cu_coordinate_id.field_id.name
                )[0] == "female":
                    text = "F"
                else:
                    text = ""
            else:
                text = str(
                    model_id.mapped(cu_coordinate_id.field_id.name)[0]
                )
        else:
            text = ""
        report.drawString(
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm,
            text
        )

    def manage_cu_coordinate_field_boolean(self, cu_coordinate_id, model_id, report):
        report.drawString(
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm,
            "X"
            if model_id.mapped(cu_coordinate_id.field_id.name)[0]
            else "",
        )

    def manage_cu_coordinate_field_float(self, cu_coordinate_id, model_id, report):
        width, height = A4
        lang_code = self.employer_id.lang
        lang = self.env["res.lang"].search([("code", "=", lang_code)])
        number = model_id.mapped(cu_coordinate_id.field_id.name)[0]
        number_format = lang.format("%.2f", number, grouping=True)
        style_right = ParagraphStyle("text", alignment=TA_RIGHT)
        paragraph_text = Paragraph(number_format, style_right)
        paragraph_text.wrapOn(report, width - 17.50 * cm, height)
        paragraph_text.drawOn(
            report,
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm
        )

    def manage_cu_coordinate_field_integer(self, cu_coordinate_id, model_id, report):
        width, height = A4
        number = str(model_id.mapped(cu_coordinate_id.field_id.name)[0])
        style_right = ParagraphStyle("text", alignment=TA_RIGHT)
        paragraph_text = Paragraph(number, style_right)
        paragraph_text.wrapOn(report, width - 17.50 * cm, height)
        paragraph_text.drawOn(
            report,
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm
        )

    def manage_cu_coordinate_field_date(self, cu_coordinate_id, model_id, report):
        if model_id.mapped(cu_coordinate_id.field_id.name)[0]:
            day = str(
                model_id.mapped(cu_coordinate_id.field_id.name)[0].day
            )
            month = str(
                model_id.mapped(cu_coordinate_id.field_id.name)[0].month
            )
            year = str(
                model_id.mapped(cu_coordinate_id.field_id.name)[0].year
            )
        else:
            day = ""
            month = ""
            year = ""
        report.drawString(
            cu_coordinate_id.coord_x * cm,
            cu_coordinate_id.coord_y * cm,
            day
        )
        report.drawString(
            (cu_coordinate_id.coord_x + 0.9) * cm,
            cu_coordinate_id.coord_y * cm,
            month
        )
        report.drawString(
            (cu_coordinate_id.coord_x + 1.5) * cm,
            cu_coordinate_id.coord_y * cm,
            year
        )

    def write_filed_on_cu(self, model_id, cu_coordinate_id, report):
        self.ensure_one()
        if cu_coordinate_id.field_id.ttype == "many2one":
            self.manage_cu_coordinate_field_many2one(cu_coordinate_id, model_id, report)
        elif cu_coordinate_id.field_id.ttype == "selection":
            self.manage_cu_coordinate_field_selection(cu_coordinate_id, model_id, report)
        elif cu_coordinate_id.field_id.ttype == "boolean":
            self.manage_cu_coordinate_field_boolean(cu_coordinate_id, model_id, report)
        elif cu_coordinate_id.field_id.ttype == "float":
            self.manage_cu_coordinate_field_float(cu_coordinate_id, model_id, report)
        elif cu_coordinate_id.field_id.ttype == "integer":
            self.manage_cu_coordinate_field_integer(cu_coordinate_id, model_id, report)
        elif cu_coordinate_id.field_id.ttype == "date":
            self.manage_cu_coordinate_field_date(cu_coordinate_id, model_id, report)
        else:
            report.drawString(
                cu_coordinate_id.coord_x * cm,
                cu_coordinate_id.coord_y * cm,
                str(model_id.mapped(cu_coordinate_id.field_id.name)[0])
                if model_id.mapped(cu_coordinate_id.field_id.name)[0]
                else ""
            )
