from django.db import migrations


def backfill_location_and_cleanup(apps, schema_editor):
    Equipment = apps.get_model('equipment', 'Equipment')
    db_alias = schema_editor.connection.alias

    no_location_ids = []
    updated_count = 0

    for eq in Equipment.objects.using(db_alias).all():
        if eq.room_id:
            from django.db import connections
            with connections[db_alias].cursor() as cursor:
                cursor.execute(
                    'SELECT floor_id FROM room WHERE id = %s', [eq.room_id]
                )
                row = cursor.fetchone()
                if row:
                    floor_id = row[0]
                    with connections[db_alias].cursor() as cursor2:
                        cursor2.execute(
                            'SELECT building_id FROM floor WHERE id = %s', [floor_id]
                        )
                        floor_row = cursor2.fetchone()
                        if floor_row:
                            building_id = floor_row[0]
                            if not eq.building_id or not eq.floor_id:
                                eq.building_id = building_id
                                eq.floor_id = floor_id
                                eq.save()
                                updated_count += 1
        if not eq.room_id and not eq.building_id and not eq.floor_id:
            no_location_ids.append(eq.id)

    if no_location_ids:
        Equipment.objects.using(db_alias).filter(id__in=no_location_ids).delete()

    print(f'Backfilled {updated_count} equipment records with building/floor from room.')
    print(f'Deleted {len(no_location_ids)} equipment records without any location.')


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0015_equipment_building_equipment_floor_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_location_and_cleanup, migrations.RunPython.noop),
    ]
