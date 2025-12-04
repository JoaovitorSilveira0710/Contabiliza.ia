# Generated migration for SEFAZ-PR compliance fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_invoice_cfop_invoice_issuer_address_and_more'),
    ]

    operations = [
        # Campos de transporte
        migrations.AddField(
            model_name='invoice',
            name='freight_mode',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('0', '0-Emitente'),
                    ('1', '1-Destinatário'),
                    ('2', '2-Terceiros'),
                    ('3', '3-Próprio remetente'),
                    ('4', '4-Próprio destinatário'),
                    ('9', '9-Sem frete'),
                ],
                default='9',
                verbose_name='Modalidade do Frete'
            ),
        ),
        
        # Campos de pagamento
        migrations.AddField(
            model_name='invoice',
            name='payment_indicator',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('0', '0-À vista'),
                    ('1', '1-À prazo'),
                ],
                default='0',
                verbose_name='Indicador de Pagamento'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment_method',
            field=models.CharField(
                max_length=2,
                choices=[
                    ('01', '01-Dinheiro'),
                    ('02', '02-Cheque'),
                    ('03', '03-Cartão Crédito'),
                    ('04', '04-Cartão Débito'),
                    ('05', '05-Crédito Loja'),
                    ('10', '10-Vale Alimentação'),
                    ('11', '11-Vale Refeição'),
                    ('12', '12-Vale Presente'),
                    ('13', '13-Vale Combustível'),
                    ('14', '14-Duplicata Mercantil'),
                    ('15', '15-Boleto Bancário'),
                    ('90', '90-Sem pagamento'),
                    ('99', '99-Outros'),
                ],
                default='99',
                verbose_name='Meio de Pagamento'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment_description',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                verbose_name='Descrição do Pagamento'
            ),
        ),
        
        # Indicadores específicos
        migrations.AddField(
            model_name='invoice',
            name='final_consumer_indicator',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('0', '0-Normal'),
                    ('1', '1-Consumidor Final'),
                ],
                default='0',
                verbose_name='Indicador Consumidor Final'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='presence_indicator',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('0', '0-Não se aplica'),
                    ('1', '1-Presencial'),
                    ('2', '2-Internet'),
                    ('3', '3-Teleatendimento'),
                    ('4', '4-Entrega domicílio'),
                    ('9', '9-Outros'),
                ],
                default='0',
                verbose_name='Indicador de Presença'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='destination_indicator',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('1', '1-Interna'),
                    ('2', '2-Interestadual'),
                    ('3', '3-Exterior'),
                ],
                default='1',
                verbose_name='Indicador Destino'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='receiver_ie_indicator',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('1', '1-Contribuinte ICMS'),
                    ('2', '2-Isento'),
                    ('9', '9-Não Contribuinte'),
                ],
                default='9',
                verbose_name='Indicador IE Destinatário'
            ),
        ),
        
        # Regime tributário CRT
        migrations.AddField(
            model_name='invoice',
            name='tax_regime',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('1', '1-Simples Nacional'),
                    ('2', '2-Simples Nacional - excesso'),
                    ('3', '3-Regime Normal'),
                ],
                default='3',
                verbose_name='Código Regime Tributário'
            ),
        ),
        
        # Ambiente
        migrations.AddField(
            model_name='invoice',
            name='environment',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('1', '1-Produção'),
                    ('2', '2-Homologação'),
                ],
                default='2',
                verbose_name='Ambiente'
            ),
        ),
        
        # Responsável técnico (opcional)
        migrations.AddField(
            model_name='invoice',
            name='tech_cnpj',
            field=models.CharField(
                max_length=14,
                blank=True,
                null=True,
                verbose_name='CNPJ Resp. Técnico'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tech_contact',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                verbose_name='Contato Resp. Técnico'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tech_email',
            field=models.EmailField(
                blank=True,
                null=True,
                verbose_name='Email Resp. Técnico'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tech_phone',
            field=models.CharField(
                max_length=14,
                blank=True,
                null=True,
                verbose_name='Fone Resp. Técnico'
            ),
        ),
        
        # Campos de InvoiceItem - CST específicos
        migrations.AddField(
            model_name='invoiceitem',
            name='icms_origin',
            field=models.CharField(
                max_length=1,
                choices=[
                    ('0', '0-Nacional'),
                    ('1', '1-Estrangeira - Importação direta'),
                    ('2', '2-Estrangeira - Mercado interno'),
                    ('3', '3-Nacional com Conteúdo > 40% e <= 70%'),
                    ('4', '4-Nacional - Processos produtivos básicos'),
                    ('5', '5-Nacional com Conteúdo < 40%'),
                    ('6', '6-Estrangeira - Importação direta sem similar'),
                    ('7', '7-Estrangeira - Mercado interno sem similar'),
                    ('8', '8-Nacional com Conteúdo > 70%'),
                ],
                default='0',
                verbose_name='Origem da Mercadoria'
            ),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='icms_cst',
            field=models.CharField(
                max_length=3,
                default='00',
                verbose_name='CST ICMS',
                help_text='00, 10, 20, 30, 40, 41, 50, 51, 60, 70, 90 ou CSOSN para Simples Nacional'
            ),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='pis_cst',
            field=models.CharField(
                max_length=2,
                default='01',
                verbose_name='CST PIS',
                help_text='01-49, 50-56, 60-66, 70-75, 98-99'
            ),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='cofins_cst',
            field=models.CharField(
                max_length=2,
                default='01',
                verbose_name='CST COFINS',
                help_text='01-49, 50-56, 60-66, 70-75, 98-99'
            ),
        ),
    ]
