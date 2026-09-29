from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0012_equipment_supplier'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Campus'),
                migrations.DeleteModel(name='Building'),
                migrations.DeleteModel(name='Floor'),
            ],
            database_operations=[],
        )
    ]
