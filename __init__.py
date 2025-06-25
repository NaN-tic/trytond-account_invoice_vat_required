# This file is part account_invoice_vat_required module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import invoice, party

def register():
    Pool.register(
        invoice.Invoice,
        party.Party,
        module='account_invoice_vat_required', type_='model')
    Pool.register(
        module='account_invoice_vat_required', type_='wizard')
    Pool.register(
        module='account_invoice_vat_required', type_='report')
