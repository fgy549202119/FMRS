from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from equipment.models import EquipmentType
from location.models import Campus, Building, Floor
from users.models import User, Administrator
from repair.models import RepairStaff


class Command(BaseCommand):
    help = '初始化佳木斯大学FMRS系统基础数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n--- 清理旧位置数据 ---'))
        Floor.objects.all().delete()
        Building.objects.all().delete()
        Campus.objects.all().delete()
        self.stdout.write('  ✅ 已清理')
        self.init_campus()
        self.init_buildings()
        self.init_floors()
        self.init_equipment_types()
        self.create_test_users()

        self.stdout.write(self.style.SUCCESS('\n========== 初始化完成 =========='))

    def init_campus(self):
        self.stdout.write(self.style.WARNING('\n--- 初始化院区数据 ---'))
        campuses = [
            {'name': 'A院', 'code': 'A', 'description': '主教学区', 'sort_order': 1},
            {'name': 'B院', 'code': 'B', 'description': '综合服务区', 'sort_order': 2},
            {'name': 'C院', 'code': 'C', 'description': '信息工程区', 'sort_order': 3},
            {'name': 'D院', 'code': 'D', 'description': '医学实验区', 'sort_order': 4},
        ]
        for item in campuses:
            obj, created = Campus.objects.update_or_create(code=item['code'], defaults=item)
            action = '创建' if created else '更新'
            self.stdout.write(f'  {action}院区: {item["name"]}')

    def init_buildings(self):
        self.stdout.write(self.style.WARNING('\n--- 初始化楼栋数据 ---'))
        campus_map = {c.code: c for c in Campus.objects.all()}

        buildings_data = [
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

        for campus_code, name, code in buildings_data:
            campus = campus_map.get(campus_code)
            if not campus: continue
            obj, created = Building.objects.update_or_create(
                code=code,
                defaults={'campus': campus, 'name': name}
            )
            action = '创建' if created else '更新'
            self.stdout.write(f'  {action}楼栋: {name} ({campus_code}院)')

    def init_floors(self):
        self.stdout.write(self.style.WARNING('\n--- 初始化楼层数据 ---'))
        building_map = {b.code: b for b in Building.objects.all()}
        floor_config = {
            'A-A1': 7, 'A-A2': 6, 'A-LAB1': 7, 'A-CANT1': 2,
            'B-LIB': 8, 'B-CANT2': 2, 'B-B1': 7, 'B-LAB1': 7,
            'C-INFO1': 6, 'C-C1': 6, 'C-LAB1': 7,
            'D-MEDLAB': 7, 'D-D1': 7,
        }
        total_floors = 0
        for bld_code, floor_count in floor_config.items():
            bld = building_map.get(bld_code)
            if not bld: continue
            for fnum in range(1, floor_count + 1):
                Floor.objects.get_or_create(
                    campus=bld.campus,
                    building=bld,
                    floor_number=fnum
                )
                total_floors += 1
        self.stdout.write(f'  ✅ 初始化 {total_floors} 个楼层')

    def init_equipment_types(self):
        self.stdout.write(self.style.WARNING('\n--- 初始化设备类型 ---'))

        equipment_types = [
            {'type_name': '水电设施', 'type_code': 'water_electric',
             'icon': 'Lightning', 'description': '水电管线、插座、开关等', 'sort_order': 1, 'status': 'active'},
            {'type_name': '门窗设施', 'type_code': 'door_window',
             'icon': 'House', 'description': '门、窗、门锁、窗帘等', 'sort_order': 2, 'status': 'active'},
            {'type_name': '教学多媒体', 'type_code': 'multimedia',
             'icon': 'Monitor', 'description': '投影仪、电子白板、音响等', 'sort_order': 3, 'status': 'active'},
            {'type_name': '网络通信设备', 'type_code': 'network',
             'icon': 'Connection', 'description': '路由器、交换机、无线AP等', 'sort_order': 4, 'status': 'active'},
            {'type_name': '宿舍家具', 'type_code': 'dorm_furniture',
             'icon': 'Suitcase', 'description': '床铺、桌椅、衣柜等', 'sort_order': 5, 'status': 'active'},
            {'type_name': '监控安防设备', 'type_code': 'security',
             'icon': 'View', 'description': '摄像头、门禁系统等', 'sort_order': 6, 'status': 'active'},
            {'type_name': '实验仪器设备', 'type_code': 'lab_equipment',
             'icon': 'Reading', 'description': '实验室仪器、实验台等', 'sort_order': 7, 'status': 'active'},
            {'type_name': '体育健身器材', 'type_code': 'sports',
             'icon': 'Coin', 'description': '篮球架、跑步机等', 'sort_order': 8, 'status': 'active'},
            {'type_name': '餐饮厨房设备', 'type_code': 'canteen',
             'icon': 'Bowl', 'description': '灶具、冰箱、消毒柜等', 'sort_order': 9, 'status': 'active'},
        ]

        for item in equipment_types:
            EquipmentType.objects.update_or_create(
                type_name=item['type_name'],
                defaults={
                    'type_code': item['type_code'],
                    'icon': item['icon'],
                    'description': item['description'],
                    'sort_order': item['sort_order'],
                    'status': item['status']
                }
            )
        self.stdout.write(f'  ✅ 初始化 {len(equipment_types)} 种设备类型')

    def create_test_users(self):
        self.stdout.write(self.style.WARNING('\n--- 创建测试用户 ---'))

        test_users = [
            {'username': 'admin', 'password': '123456', 'real_name': '系统管理员',
             'user_type': 'admin', 'phone': '13800000000', 'is_staff': True, 'is_superuser': True},
            {'username': '100', 'password': '123456', 'real_name': '张老师',
             'user_type': 'teacher', 'phone': '13900000001'},
            {'username': '101', 'password': '123456', 'real_name': '王老师',
             'user_type': 'teacher', 'phone': '13900000002'},
            {'username': '2026001', 'password': '123456', 'real_name': '李同学',
             'user_type': 'student', 'phone': '13700000001'},
            {'username': '2026002', 'password': '123456', 'real_name': '赵同学',
             'user_type': 'student', 'phone': '13700000002'},
        ]

        for user_data in test_users:
            password = user_data.pop('password')
            user, created = User.objects.update_or_create(username=user_data['username'], defaults=user_data)
            user.set_password(password)
            user.save()
            action = '创建' if created else '更新'
            self.stdout.write(f'  ✅ {action}用户: {user_data["real_name"]}')

        staff_list = [
            {'staff_no': '13800000001', 'name': '王维修', 'phone': '13800000001'},
            {'staff_no': '13800000002', 'name': '刘维修', 'phone': '13800000002'},
            {'staff_no': '13800000003', 'name': '赵维修', 'phone': '13800000003'},
            {'staff_no': '13800000004', 'name': '钱维修', 'phone': '13800000004'},
        ]
        for sd in staff_list:
            RepairStaff.objects.update_or_create(
                staff_no=sd['staff_no'],
                defaults={'real_name': sd['name'], 'phone': sd['phone'], 'password': make_password('123456')}
            )
            self.stdout.write(f'  🔧 创建/更新维修员: {sd["name"]}')

        Administrator.objects.update_or_create(
            admin_no='admin',
            defaults={'real_name': '系统管理员', 'phone': '13800000000', 'password': make_password('123456')}
        )
        self.stdout.write(f'  👤 创建/更新管理员')
