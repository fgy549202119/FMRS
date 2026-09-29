from django.db import migrations, models
import django.db.models.deletion


def convert_equipment_type_fk(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM knowledge_base LIKE 'equipment_type_id'")
        col_info = cursor.fetchone()
        if col_info:
            col_type = col_info[1]
            if 'varchar' in col_type.lower():
                cursor.execute("ALTER TABLE knowledge_base DROP COLUMN equipment_type_id")
                cursor.execute("ALTER TABLE knowledge_base ADD COLUMN equipment_type_id bigint NULL")
                cursor.execute(
                    "ALTER TABLE knowledge_base ADD CONSTRAINT fk_kb_equipment_type "
                    "FOREIGN KEY (equipment_type_id) REFERENCES equipment_type(id) ON DELETE SET NULL"
                )


def reverse_convert(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE knowledge_base DROP FOREIGN KEY fk_kb_equipment_type")
        cursor.execute("ALTER TABLE knowledge_base DROP COLUMN equipment_type_id")
        cursor.execute("ALTER TABLE knowledge_base ADD COLUMN equipment_type_id varchar(100) NOT NULL DEFAULT ''")


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0011_image_textfield'),
        ('common', '0002_remove_sparepart_category_remove_sparepart_max_stock_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='repairsparepart',
            options={'ordering': ['-created_at'], 'verbose_name': '维修备件使用', 'verbose_name_plural': '维修备件使用'},
        ),
        migrations.RunPython(convert_equipment_type_fk, reverse_convert),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
