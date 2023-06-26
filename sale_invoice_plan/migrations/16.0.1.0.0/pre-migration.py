# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade

_column_renames = {
    "sale_invoice_plan_invoice_rel": [
        ("invoice_id", "move_id"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "sale_invoice_plan_invoice_rel", "invoice_id"):
        openupgrade.rename_columns(env.cr, _column_renames)
