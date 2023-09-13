from openupgradelib import openupgrade


def update_account_cu_statement_type_2022(env):

    acst_2022 = env.ref("l10n_it_cu.account_cu_statement_type_se_2022")
    query_2022 = """
            UPDATE 
                account_cu_statement acs
            SET 
                acs.statement_type_id = %(id_acst_2022)s
            WHERE 
                acs.statement_type_id IN (
                    SELECT 
                        id 
                    FROM 
                        account_cu_statement_type 
                    WHERE 
                        name = %(name_acst_2022)s
                )
        """ % {
        "id_acst_2022": acst_2022.id,
        "name_acst_2022": acst_2022.name,
    }

    openupgrade.logged_query(env.cr, query_2022)


def update_account_cu_statement_type_2023(env):

    acst_2023 = env.ref("l10n_it_cu.account_cu_statement_type_se_2023")
    query_2023 = """
        UPDATE 
            account_cu_statement acs
        SET 
            acs.statement_type_id = %(id_acst_2023)s
        WHERE 
            acs.statement_type_id IN (
                SELECT 
                    id 
                FROM 
                    account_cu_statement_type 
                WHERE 
                    name = %(name_acst_2023)s
            )
    """ % {
        "id_acst_2023": acst_2023.id,
        "name_acst_2023": acst_2023.name,
    }

    openupgrade.logged_query(env.cr, query_2023)


@openupgrade.migrate()
def migrate(env, installed_version):

    update_account_cu_statement_type_2022(env)
    update_account_cu_statement_type_2023(env)
