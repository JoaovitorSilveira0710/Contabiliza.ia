from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from invoices.models import Invoice, InvoiceItem
from invoices.services.xml_generator import NFeGenerator
from clients.models import Client


class NFeGeneratorTestCase(TestCase):
    """Tests for NF-e XML generator SEFAZ-PR standard"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client.objects.create(
            person_type='PJ',
            name='COOPERATIVA AGRARIA AGROINDUSTRIAL',
            tax_id='77.890.846/0027-08',
            state_registration='4010717170',
            email='teste@agraria.com.br',
            phone='46999999999',
            zip_code='85031-350',
            street='Rodovia BR-277',
            number='01',
            neighborhood='Jardim das Americas',
            city='Guarapuava',
            state='PR'
        )
        
        self.invoice = Invoice.objects.create(
            number='3488216',
            series='890',
            invoice_type='nfe',
            model_code='55',
            operation_nature='venda_soja',
            operation_type='saida',
            cfop='5101',
            
            issuer_name='CLAUDIO VIRMOND KIRYLA',
            issuer_tax_id='532.134.679-87',
            issuer_state_registration='9534062092',
            issuer_address='Lagoa Seca',
            issuer_number='S/N',
            issuer_district='Lagoa Seca',
            issuer_city='Candoi',
            issuer_city_code='4104428',
            issuer_state='PR',
            issuer_zip_code='85140-000',
            
            client=self.client,
            receiver_city_code='4109401',
            
            issue_date=timezone.now(),
            
            total_products=Decimal('114604.60'),
            total_services=Decimal('0'),
            discount=Decimal('0'),
            shipping=Decimal('0'),
            insurance=Decimal('0'),
            other_expenses=Decimal('0'),
            
            icms_base=Decimal('0'),
            icms_value=Decimal('0'),
            ipi_value=Decimal('0'),
            pis_value=Decimal('0'),
            cofins_value=Decimal('0'),
            iss_value=Decimal('0'),
            
            total_value=Decimal('114604.60'),
            
            status='draft',
            
            freight_mode='1',
            payment_indicator='0',
            payment_method='99',
            payment_description='Nota de Produtor',
            final_consumer_indicator='0',
            presence_indicator='0',
            destination_indicator='1',
            receiver_ie_indicator='1',
            tax_regime='3',
            environment='2',
        )
        
        self.item = InvoiceItem.objects.create(
            invoice=self.invoice,
            item_type='product',
            code='0115.0010.00',
            description='SOJA EM GRAO',
            ncm='12019000',
            cfop='5101',
            unit='kg',
            quantity=Decimal('50710.0000'),
            unit_value=Decimal('2.26'),
            total_value=Decimal('114604.60'),
            discount=Decimal('0'),
            
            # Impostos
            icms_origin='0',  # Nacional
            icms_cst='90',
            icms_rate=Decimal('0'),
            icms_value=Decimal('0'),
            
            pis_cst='08',
            pis_rate=Decimal('0'),
            pis_value=Decimal('0'),
            
            cofins_cst='08',
            cofins_rate=Decimal('0'),
            cofins_value=Decimal('0'),
        )
    
    def test_generate_access_key(self):
        """Test generation of 44-digit access key"""
        generator = NFeGenerator(self.invoice)
        access_key = generator.generate_access_key()
        
        self.assertEqual(len(access_key), 44)
        self.assertTrue(access_key.isdigit())
        
        self.assertEqual(access_key[0:2], '41')
        
        self.assertEqual(access_key[20:22], '55')
    
    def test_generate_xml_structure(self):
        """Test basic structure of generated XML"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<NFe xmlns="http://www.portalfiscal.inf.br/nfe">', xml_string)
        self.assertIn('<infNFe', xml_string)
        self.assertIn('<ide>', xml_string)
        self.assertIn('<emit>', xml_string)
        self.assertIn('<dest>', xml_string)
        self.assertIn('<det nItem="1">', xml_string)
        self.assertIn('<total>', xml_string)
        self.assertIn('<transp>', xml_string)
        self.assertIn('<pag>', xml_string)
        
        self.assertIn('<cUF>41</cUF>', xml_string)
        self.assertIn('<UF>PR</UF>', xml_string)
        
        self.assertIn('<cMunFG>4104428</cMunFG>', xml_string)
        
        # Verificar modalidade frete
        self.assertIn('<modFrete>1</modFrete>', xml_string)
        
        # Verificar pagamento
        self.assertIn('<tPag>99</tPag>', xml_string)
        self.assertIn('<xPag>Nota de Produtor</xPag>', xml_string)
    
    def test_generate_xml_icms90(self):
        """Test generation of ICMS CST 90 (Others)"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<ICMS90>', xml_string)
        self.assertIn('<orig>0</orig>', xml_string)
        self.assertIn('<CST>90</CST>', xml_string)
    
    def test_generate_xml_pis_cofins_nt(self):
        """Test generation of non-taxable PIS/COFINS (CST 08)"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<PISNT>', xml_string)
        self.assertIn('<CST>08</CST>', xml_string)
        
        self.assertIn('<COFINSNT>', xml_string)
    
    def test_generate_xml_totals(self):
        """Test totals according to PR standard"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<vFCPUFDest>0.00</vFCPUFDest>', xml_string)
        self.assertIn('<vICMSUFDest>0.00</vICMSUFDest>', xml_string)
        self.assertIn('<vICMSUFRemet>0.00</vICMSUFRemet>', xml_string)
        
        self.assertIn('<vNF>114604.60</vNF>', xml_string)
        self.assertIn('<vProd>114604.60</vProd>', xml_string)
    
    def test_generate_xml_with_cpf_emitter(self):
        """Test generation with CPF issuer (rural producer)"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<CPF>53213467987</CPF>', xml_string)
    
    def test_generate_xml_ind_ie_dest(self):
        """Test receiver IE indicator"""
        generator = NFeGenerator(self.invoice)
        xml_string = generator.generate_xml()
        
        self.assertIn('<indIEDest>1</indIEDest>', xml_string)
        
        self.assertIn('<IE>4010717170</IE>', xml_string)
    
    def test_xml_saves_to_file(self):
        """Test if XML is saved to xml_file field"""
        generator = NFeGenerator(self.invoice)
        generator.generate_xml()
        
        self.invoice.refresh_from_db()
        
        self.assertTrue(self.invoice.xml_file)
        self.assertIn('NFe3488216_890', self.invoice.xml_file.name)
        self.assertTrue(self.invoice.xml_file.name.endswith('.xml'))
    
    def test_access_key_persistence(self):
        """Test if access key is persisted to database"""
        self.invoice.access_key = None
        self.invoice.save()
        self.assertIsNone(self.invoice.access_key)
        
        generator = NFeGenerator(self.invoice)
        generator.generate_xml()
        
        self.invoice.refresh_from_db()
        self.invoice.refresh_from_db()
        
        # Verificar se foi salva
        self.assertIsNotNone(self.invoice.access_key)
        self.assertEqual(len(self.invoice.access_key), 44)


class InvoiceModelTestCase(TestCase):
    """Testes para o modelo Invoice com campos SEFAZ-PR"""
    
    def test_new_fields_exist(self):
        """Testa se os novos campos existem no modelo"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'invoices_invoice'
            """)
            columns = [row[0] for row in cursor.fetchall()]
        
        # Verificar campos novos
        expected_fields = [
            'freight_mode',
            'payment_indicator',
            'payment_method',
            'payment_description',
            'final_consumer_indicator',
            'presence_indicator',
            'destination_indicator',
            'receiver_ie_indicator',
            'tax_regime',
            'environment',
        ]
        
        for field in expected_fields:
            self.assertIn(field, columns, f"Campo {field} não encontrado no banco")
