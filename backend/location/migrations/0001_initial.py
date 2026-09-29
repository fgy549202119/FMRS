from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Building',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=100, verbose_name='楼栋名称')),
                        ('code', models.CharField(max_length=50, unique=True, verbose_name='楼栋编码')),
                    ],
                    options={
                        'verbose_name': '楼栋',
                        'verbose_name_plural': '楼栋',
                        'db_table': 'building',
                        'ordering': ['id'],
                    },
                ),
                migrations.CreateModel(
                    name='Campus',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=50, verbose_name='院区名称')),
                        ('code', models.CharField(max_length=20, unique=True, verbose_name='院区编码')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                        ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                    ],
                    options={
                        'verbose_name': '院区',
                        'verbose_name_plural': '院区',
                        'db_table': 'campus',
                        'ordering': ['sort_order', 'id'],
                    },
                ),
                migrations.CreateModel(
                    name='Floor',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('floor_number', models.IntegerField(verbose_name='楼层号')),
                        ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='location.building', verbose_name='所属楼栋')),
                        ('campus', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='location.campus', verbose_name='所属院区')),
                    ],
                    options={
                        'verbose_name': '楼层',
                        'verbose_name_plural': '楼层',
                        'db_table': 'floor',
                        'ordering': ['building__id', 'floor_number'],
                        'unique_together': {('building', 'floor_number')},
                    },
                ),
                migrations.AddField(
                    model_name='building',
                    name='campus',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='location.campus', verbose_name='所属院区'),
                ),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='房间名称')),
                ('sort', models.IntegerField(default=0, verbose_name='排序号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='location.floor', verbose_name='所属楼层')),
            ],
            options={
                'verbose_name': '房间',
                'verbose_name_plural': '房间',
                'db_table': 'room',
                'ordering': ['sort', 'id'],
                'unique_together': {('floor', 'name')},
            },
        ),
    ]
