# Copyright 2022-TODAY Openforce Srls Unipersonale (www.openforce.it)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Certificazione Unica',
    'version': '14.0.1.0.0',
    'category': 'Localization/Italy',
    'description': """
    Modulo per la gestione della Certificazione Unica
    """,
    'author': 'Openforce',
    'website': 'http://www.openforce.it',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_ateco',
        'l10n_it_payment_reason',
        'l10n_it_appointment_code',
        'l10n_it_withholding_tax_payment',
        'l10n_it_withholding_tax_reason',
        'partner_contact_birthdate',
        'partner_contact_birthplace',
        'partner_contact_gender',
        'partner_firstname'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_cu_statement_type.xml',
        'views/account_cu_statement.xml',
        'views/account_cu_statement_type.xml',
        'views/account_cu_se_partner.xml',
        'views/account_cu_se_partner_line.xml',
        'views/account_fiscal_position.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
