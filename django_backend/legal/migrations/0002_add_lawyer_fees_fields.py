# Generated manually for lawyer fees and court integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='legalprocess',
            name='lawyer_fee_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Percentual sobre o valor da causa', max_digits=5, null=True, verbose_name='Percentual de Honorários'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='lawyer_fee_fixed',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Honorários Fixos'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='lawyer_fee_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Honorários Pagos'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='lawyer_fee_notes',
            field=models.TextField(blank=True, verbose_name='Observações sobre Honorários'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='opposing_parties',
            field=models.TextField(blank=True, help_text='Nomes das partes contrárias separados por vírgula', verbose_name='Partes Contrárias'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='case_class',
            field=models.CharField(blank=True, max_length=100, verbose_name='Classe Processual'),
        ),
        migrations.AddField(
            model_name='legalprocess',
            name='last_sync_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Última Sincronização'),
        ),
    ]
