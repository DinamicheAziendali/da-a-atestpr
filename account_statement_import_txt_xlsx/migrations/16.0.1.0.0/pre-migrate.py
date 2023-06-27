# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_model_renames = [
    (
        "account.bank.statement.import.sheet.mapping",
        "account.statement.import.sheet.mapping",
    ),
    (
        "account.bank.statement.import.sheet.parser",
        "account.statement.import.sheet.parser",
    ),
    (
        "account.bank.statement.import.sheet.mapping.wizard",
        "account.statement.import.sheet.mapping.wizard",
    ),
]

_table_renames = [
    (
        "account_bank_statement_import_sheet_mapping",
        "account_statement_import_sheet_mapping",
    ),
    (
        "account_bank_statement_import_sheet_parser",
        "account_statement_import_sheet_parser",
    ),
    (
        "account_bank_statement_import_sheet_mapping_wizard",
        "account_statement_import_sheet_mapping_wizard",
    ),
]

_fields_to_add = [
    (
        "amount_debit_column",
        "account.statement.import.sheet.mapping",
        "account_statement_import_sheet_mapping",
        "char",
        "varchar",
        "account_statement_import_txt_xlsx",
    ),
    (
        "amount_credit_column",
        "account.statement.import.sheet.mapping",
        "account_statement_import_sheet_mapping",
        "char",
        "varchar",
        "account_statement_import_txt_xlsx",
    ),
]


def amount_to_debit_amount_and_amount2_to_credit_amount(env):
    cr = env.cr
    sql_amount2_exists = """SELECT count(id) FROM ir_model_fields
        WHERE name = 'amount2_column'
        AND model = 'account.statement.import.sheet.mapping';"""
    cr.execute(sql_amount2_exists)
    if cr.fetchone()[0] > 0:
        openupgrade.add_fields(env, _fields_to_add)
        cr.execute(
            """ALTER TABLE account_statement_import_sheet_mapping
            ALTER COLUMN amount_column DROP NOT NULL;"""
        )
        openupgrade.logged_query(
            cr,
            """
                UPDATE account_statement_import_sheet_mapping
                SET
                    amount_credit_column = amount2_column,
                    amount_debit_column = amount_column,
                    amount_column = NULL
                WHERE amount2_column IS NOT NULL;
            """,
        )


def add_fields_and_drop_not_null(env):
    cr = env.cr
    sql_debit_exists = """SELECT count(id) FROM ir_model_fields
        WHERE name = 'amount_debit_column'
        AND model = 'account.statement.import.sheet.mapping';"""
    cr.execute(sql_debit_exists)
    if cr.fetchone()[0] > 0:
        openupgrade.add_fields(env, _fields_to_add)
        cr.execute(
            """ALTER TABLE account_statement_import_sheet_mapping
            ALTER COLUMN amount_column DROP NOT NULL;"""
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    amount_to_debit_amount_and_amount2_to_credit_amount(env)
    add_fields_and_drop_not_null(env)
