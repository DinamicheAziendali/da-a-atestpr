from openupgradelib import openupgrade


def rename_old_italian_module(cr):

    openupgrade.update_module_names(
        cr,
        [
            ("assets_management", "l10n_it_asset_management"),
        ],
    )


@openupgrade.migrate()
def migrate(env, installed_version):
    if (
        not openupgrade.is_module_installed(env.cr, "assets_management")
        or openupgrade.is_module_installed(env.cr, "l10n_it_asset_management")
    ):
        return

    rename_old_italian_module(env.cr)
