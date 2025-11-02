import unittest
from decimal import Decimal

from proteus import Model
from trytond.exceptions import UserError, UserWarning
from trytond.modules.account.tests.tools import (
    create_chart,
    create_fiscalyear, create_tax,
    get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install account_invoice_vat_required Module
        activate_modules('account_invoice_vat_required')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create party with vat_required
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.vat_required = True
        party.save()

        # Create party tax identifier
        party_tax_identifier = party.identifiers.new()
        party_tax_identifier.type = 'eu_vat'
        party_tax_identifier.code = 'ESB01000009'
        party.save()

        # Create account categories
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()
        account_category_tax, = account_category.duplicate()
        account_category_tax.customer_taxes.append(tax)
        account_category_tax.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal('40')
        template.account_category = account_category_tax
        template.save()
        product, = template.products
        product.cost_price = Decimal('25')
        product.save()

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()
        # Test 1: Create invoice without tax_identifier -> UserError
        Invoice = Model.get('account.invoice')
        invoice = Invoice()
        invoice.company = company
        invoice.party = party
        invoice.payment_term = payment_term
        line = invoice.lines.new()
        line.product = product
        line.account = revenue
        line.quantity = 5
        line.unit_price = Decimal(40)
        invoice.save()
        with self.assertRaises(UserError):
            invoice.click('post')

        invoice.reload()
        self.assertEqual(invoice.state, 'draft')

        # Create company tax identifier for test 2 and 3
        company_tax_identifier = company.party.identifiers.new()
        company_tax_identifier.party = company.party
        company_tax_identifier.type = 'eu_vat'
        company_tax_identifier.code = 'ES01234567L'
        company_tax_identifier.save()

        # Test 2: Create invoice with tax_identifier but without party_tax_identifier -> UserWarning
        # Create party without tax identifier
        party2 = Party(name='Party2')
        party2.vat_required = True
        party2.save()

        invoice2 = Invoice()
        invoice2.company = company
        invoice2.party = party2
        invoice2.payment_term = payment_term
        line = invoice2.lines.new()
        line.product = product
        line.account = revenue
        line.quantity = 5
        line.unit_price = Decimal(40)
        invoice2.save()

        with self.assertRaises(UserWarning):
            invoice2.click('post')

        invoice2.reload()
        self.assertEqual(invoice2.state, 'draft')

        # Test 3: Create invoice with both tax_identifier and party_tax_identifier -> post successfully
        invoice3 = Invoice()
        invoice3.company = company
        invoice3.party = party
        invoice3.payment_term = payment_term
        invoice3.tax_identifier = company_tax_identifier
        line = invoice3.lines.new()
        line.product = product
        line.account = revenue
        line.quantity = 5
        line.unit_price = Decimal(40)
        invoice3.save()

        invoice3.click('post')
        self.assertEqual(invoice3.state, 'posted')
