from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, fields
from trytond.i18n import gettext
from trytond.exceptions import UserWarning


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    @classmethod
    @ModelView.button
    def post(cls, invoices):
        pool = Pool()
        Warning = pool.get('res.user.warning')
        to_warn = []
        for invoice in invoices:
            if not invoice.party.vat_required:
                continue
            if not invoice.party_tax_identifier:
                to_warn.append(invoice)
        if to_warn:
            key = Warning.format('not_tax_identifier', to_warn)
            names = ', '.join(
                [invoice.rec_name for invoice in to_warn])
            if Warning.check(key):
                raise UserWarning(key,
                    gettext('account_invoice_vat_required.msg_not_tax_identifier',
                            invoices=names))
        super().post(invoices)
