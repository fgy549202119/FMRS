from django.db import migrations, models
import django.db.models.deletion


def remove_category_if_exists(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM knowledge_base LIKE 'category'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE knowledge_base DROP COLUMN category")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0011_image_textfield'),
        ('common', '0003_alter_repairsparepart_options_and_more'),
    ]

    operations = [
        migrations.RunPython(remove_category_if_exists, noop),
    ]
