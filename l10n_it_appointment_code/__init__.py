from . import models

from openupgradelib import openupgrade


def rename_old_italian_module(cr):

    if not openupgrade.is_module_installed(cr, "l10n_it_codici_carica"):
        return

    openupgrade.rename_xmlids(
        cr,
        [
            (
                "l10n_it_codici_carica.view_codice_carica_tree",
                "l10n_it_appointment_code.view_appointment_code_tree",
            ),
            (
                "l10n_it_codici_carica.view_codice_carica_form",
                "l10n_it_appointment_code.view_appointment_code_form",
            ),
            (
                "l10n_it_codici_carica.action_codice_carica",
                "l10n_it_appointment_code.action_appointment_code",
            ),
            (
                "l10n_it_codici_carica.menu_codice_carica",
                "l10n_it_appointment_code.menu_appointment_code",
            ),
        ],
    )
    openupgrade.update_module_names(
        cr,
        [
            ("l10n_it_codici_carica", "l10n_it_appointment_code"),
        ],
    )
    openupgrade.rename_models(
        cr,
        [
            ("codice.carica", "appointment.code"),
        ],
    )
    openupgrade.rename_tables(
        cr,
        [
            ("codice_carica", "appointment_code"),
        ],
    )
