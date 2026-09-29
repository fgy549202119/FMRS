from django.db import migrations


def assign_sequence_numbers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT id FROM equipment ORDER BY id')
        ids = [row[0] for row in cursor.fetchall()]
        for seq, eq_id in enumerate(ids, start=1):
            cursor.execute('UPDATE equipment SET sequence_number = %s WHERE id = %s', [seq, eq_id])


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0017_add_sequence_number_remove_quantity'),
    ]

    operations = [
        migrations.RunPython(assign_sequence_numbers, reverse_migration),
    ]
