from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView
from trytond.i18n import gettext
from trytond.exceptions import UserError, UserWarning


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
            key = Warning.format('missing_tax_identifier', to_warn)
            names = ', '.join([x.rec_name for x in to_warn])
            if Warning.check(key):
                raise UserWarning(key,
                    gettext('account_invoice_vat_required.'
                        'msg_missing_party_tax_identifier', invoices=names))

        to_raise = [x for x in invoices if not x.tax_identifier]
        if to_raise:
            names = ', '.join([x.rec_name for x in to_raise])
            raise UserError(gettext('account_invoice_vat_required.'
                    'msg_missing_company_tax_identifier', invoices=names))

        super().post(invoices)
