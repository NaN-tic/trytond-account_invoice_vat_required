from trytond.pool import PoolMeta
from trytond.model import fields


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    vat_required = fields.Boolean("VAT Required")

    @staticmethod
    def default_vat_required():
        return True
