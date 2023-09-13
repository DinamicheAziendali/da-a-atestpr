# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import fields, models


class AccountCuCoordinate(models.Model):
    _name = "account.cu.coordinate"
    _description = "Account CU - Coordinate"

    statement_type_id = fields.Many2one(
        "account.cu.statement.type",
        string="CU Statement Type",
        required=True,
    )
    name = fields.Char(string="Description")
    sheet = fields.Selection([
        ("H", "Header"),
        ("F", "Front"),
        ("RX", "RX"),
    ], string="Sheet")
    coord_x = fields.Float(string="Coord. X")
    coord_y = fields.Float(string="Coord. Y")
    model_id = fields.Many2one("ir.model", string="Model")
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        copy=True,
    )
    write_once_on = fields.Selection([
        ("F", "First page"),
        ("L", "Last page"),
    ], string="Write Once On")
