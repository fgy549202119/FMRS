from django.core.management.base import BaseCommand
from location.models import Campus, Building, Floor


class Command(BaseCommand):
    help = 'Initialize campus location data: 4 campuses, 13 buildings, floors'

    def handle(self, *args, **options):
        Campus.objects.all().delete()
        Building.objects.all().delete()
        Floor.objects.all().delete()

        campuses = {}
        campus_data = [
            {'name': 'A院', 'code': 'A', 'description': '主教学区', 'sort_order': 1},
            {'name': 'B院', 'code': 'B', 'description': '综合服务区', 'sort_order': 2},
            {'name': 'C院', 'code': 'C', 'description': '信息工程区', 'sort_order': 3},
            {'name': 'D院', 'code': 'D', 'description': '医学实验区', 'sort_order': 4},
        ]
        for cd in campus_data:
            c = Campus.objects.create(**cd)
            campuses[c.code] = c
            self.stdout.write(f'  Created campus: {c.name} (id={c.id})')

        buildings = {}
        building_data = [
            ('A', 'A1教学楼', 'A-A1'),
            ('A', 'A2教学楼', 'A-A2'),
            ('A', 'A1实验楼', 'A-LAB1'),
            ('A', '第一食堂', 'A-CANT1'),
            ('B', '图书馆', 'B-LIB'),
            ('B', '第二食堂', 'B-CANT2'),
            ('B', 'B1教学楼', 'B-B1'),
            ('B', 'B1实验楼', 'B-LAB1'),
            ('C', 'C1信息楼', 'C-INFO1'),
            ('C', 'C1教学楼', 'C-C1'),
            ('C', 'C1实验楼', 'C-LAB1'),
            ('D', '医学实验楼', 'D-MEDLAB'),
            ('D', 'D1教学楼', 'D-D1'),
        ]
        for campus_code, name, code in building_data:
            b = Building.objects.create(campus=campuses[campus_code], name=name, code=code)
            buildings[code] = b
            self.stdout.write(f'  Created building: {b} (id={b.id})')

        floor_config = {
            'A-A1': 7, 'A-A2': 6, 'A-LAB1': 7, 'A-CANT1': 2,
            'B-LIB': 8, 'B-CANT2': 2, 'B-B1': 7, 'B-LAB1': 7,
            'C-INFO1': 6, 'C-C1': 6, 'C-LAB1': 7,
            'D-MEDLAB': 7, 'D-D1': 7,
        }
        total_floors = 0
        for bld_code, floor_count in floor_config.items():
            bld = buildings[bld_code]
            for fnum in range(1, floor_count + 1):
                Floor.objects.create(
                    campus=bld.campus,
                    building=bld,
                    floor_number=fnum
                )
                total_floors += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nInitialization complete!\n'
            f'  Campuses: {Campus.objects.count()}\n'
            f'  Buildings: {Building.objects.count()}\n'
            f'  Floors: {total_floors}'
        ))
