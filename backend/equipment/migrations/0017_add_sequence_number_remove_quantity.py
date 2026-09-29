from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0016_backfill_location_and_cleanup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='equipment',
            options={'ordering': ['sequence_number'], 'verbose_name': '公共设备', 'verbose_name_plural': '公共设备'},
        ),
        migrations.AddField(
            model_name='equipment',
            name='sequence_number',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='设备序号'),
        ),
    ]
