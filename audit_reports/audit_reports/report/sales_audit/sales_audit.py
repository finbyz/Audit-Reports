# sales_audit.py
from frappe import _
import frappe
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": _("SO Date"), "fieldname": "so_date", "fieldtype": "Date", "width": 120},
        {"label": _("SO Amount"), "fieldname": "so_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("SI Date"), "fieldname": "si_date", "fieldtype": "Date", "width": 120},
        {"label": _("SI Amount"), "fieldname": "si_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": _("DN Date"), "fieldname": "dn_date", "fieldtype": "Date", "width": 120},
        {"label": _("DN Amount"), "fieldname": "dn_amount", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    query = """
        SELECT
            so_item.item_code AS item_code,
            so_item.parent AS sales_order,
            so_item.creation AS so_date,
            so_item.amount AS so_amount,
            si_item.parent AS sales_invoice,
            si.posting_date AS si_date,
            si_item.amount AS si_amount,
            dn_item.parent AS delivery_note,
            dn.posting_date AS dn_date,
            dn_item.amount AS dn_amount
        FROM
            `tabSales Order Item` so_item
        LEFT JOIN
            `tabSales Invoice Item` si_item
            ON so_item.item_code = si_item.item_code AND so_item.parent = si_item.sales_order
        LEFT JOIN
            `tabSales Invoice` si
            ON si_item.parent = si.name
        LEFT JOIN
            `tabDelivery Note Item` dn_item
            ON so_item.item_code = dn_item.item_code AND so_item.parent = dn_item.against_sales_order
        LEFT JOIN
            `tabDelivery Note` dn
            ON dn_item.parent = dn.name
        WHERE
            (ABS(IFNULL(so_item.amount, 0) - IFNULL(si_item.amount, 0)) > 0
            OR ABS(IFNULL(so_item.amount, 0) - IFNULL(dn_item.amount, 0)) > 0
            OR ABS(IFNULL(si_item.amount, 0) - IFNULL(dn_item.amount, 0)) > 0)
    """
    if filters.get("from_date") and filters.get("to_date"):
        query += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    query += " ORDER BY so_item.item_code, so_item.parent"

    return frappe.db.sql(query, filters, as_dict=True)
