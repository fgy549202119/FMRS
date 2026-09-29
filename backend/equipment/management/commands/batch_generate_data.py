from django.core.management.base import BaseCommand
from django.db import transaction
from location.models import Campus, Building, Floor, Room
from equipment.models import EquipmentType, Equipment


EQUIPMENT_PARAMS = {
    '暖气': {
        'type_name': '空调暖通设备',
        'specification': '圣劳伦斯 钢制板式散热器 600*1200mm',
        'supplier': '圣劳伦斯暖通科技有限公司',
    },
    '空调': {
        'type_name': '空调暖通设备',
        'specification': '格力 KFR-35GW/(35592)FNhAa-B1 1.5匹变频冷暖',
        'supplier': '珠海格力电器股份有限公司',
    },
    '音响': {
        'type_name': '教学设施',
        'specification': '漫步者 R101V 2.1声道多媒体音箱',
        'supplier': '深圳市漫步者科技股份有限公司',
    },
    '监控': {
        'type_name': '安全设施',
        'specification': '海康威视 DS-2CD3T46WD-I3 400万像素网络摄像头',
        'supplier': '杭州海康威视数字技术股份有限公司',
    },
    '门锁': {
        'type_name': '门窗设施',
        'specification': '凯迪仕 K20-V 指纹密码智能门锁',
        'supplier': '深圳市凯迪仕智能科技股份有限公司',
    },
    '投影仪': {
        'type_name': '教学设施',
        'specification': '爱普生 CB-X50 3600流明XGA办公投影仪',
        'supplier': '爱普生(中国)有限公司',
    },
    '教学主机': {
        'type_name': '教学设施',
        'specification': '联想 启天M450 i5-12400/8G/512G/Win11',
        'supplier': '联想(北京)有限公司',
    },
    '路由器': {
        'type_name': '网络设备',
        'specification': 'H3C ER3200G3 1×GE Combo WAN+4×GE LAN 全千兆企业级',
        'supplier': '新华三技术有限公司',
    },
    '打印机': {
        'type_name': '教学设施',
        'specification': '爱普生 L3255 墨仓式彩色喷墨一体机',
        'supplier': '爱普生(中国)有限公司',
    },
}

FULL_ROOM_EQUIPMENT = [
    ('暖气', 2), ('空调', 2), ('音响', 4), ('监控', 5),
    ('门锁', 2), ('投影仪', 1), ('教学主机', 1), ('路由器', 1),
]

FULL_ROOM_EQUIPMENT_NO_HOST = [
    ('暖气', 2), ('空调', 2), ('音响', 4), ('监控', 5),
    ('门锁', 2), ('投影仪', 1), ('路由器', 1),
]

SIMPLE_ROOM_EQUIPMENT = [
    ('暖气', 2), ('门锁', 1), ('路由器', 1),
]

CAFETERIA_FLOOR_EQUIPMENT = [
    ('路由器', 1),
]

PRINTER_RULE = ('打印机', 1)

EXCLUDED_BUILDINGS = ['第一食堂', '第二食堂']
LIBRARY_BUILDINGS = ['图书馆']

FULL_EQUIPMENT_BUILDINGS = [
    'A1教学楼', 'A2教学楼', 'A1实验楼',
    'B1教学楼', 'B1实验楼',
    'C1信息楼', 'C1教学楼', 'C1实验楼',
    '医学实验楼', 'D1教学楼',
]


class Command(BaseCommand):
    help = '批量生成房间和设备数据'

    def add_arguments(self, parser):
        parser.add_argument('--rooms-only', action='store_true', help='仅生成房间数据')
        parser.add_argument('--equipment-only', action='store_true', help='仅生成设备数据')

    def handle(self, *args, **options):
        rooms_only = options.get('rooms_only', False)
        equipment_only = options.get('equipment_only', False)

        self.stdout.write(self.style.NOTICE('===== 开始批量生成数据 ====='))

        room_count = 0
        room_skipped = 0
        equip_count = 0
        equip_skipped = 0

        if not equipment_only:
            self.stdout.write(self.style.NOTICE('\n--- 任务1: 批量生成房间 ---'))
            room_count, room_skipped = self.generate_rooms()

        if not rooms_only:
            self.stdout.write(self.style.NOTICE('\n--- 任务2: 批量生成设备 ---'))
            equip_count, equip_skipped = self.generate_equipment()

        self.stdout.write(self.style.SUCCESS(
            f'\n===== 完成 =====\n'
            f'本次共生成 {room_count} 个房间，{equip_count} 台设备\n'
            f'跳过 {room_skipped + equip_skipped} 条重复数据'
        ))

    def generate_rooms(self):
        total_created = 0
        total_skipped = 0

        buildings = Building.objects.select_related('campus').all()
        for building in buildings:
            if building.name in EXCLUDED_BUILDINGS:
                self.stdout.write(f'  [跳过] {building.name} (食堂不生成房间)')
                continue

            floors = Floor.objects.filter(building=building).order_by('floor_number')
            for floor in floors:
                for seq in range(1, 21):
                    room_name = f'{floor.floor_number}{seq:02d}'
                    _, created = Room.objects.get_or_create(
                        floor=floor,
                        name=room_name,
                        defaults={'sort': int(f'{floor.floor_number}{seq:02d}')}
                    )
                    if created:
                        total_created += 1
                    else:
                        total_skipped += 1
                        self.stdout.write(
                            f'  [跳过] {building.name} {floor.floor_number}层 {room_name}已存在'
                        )

            self.stdout.write(self.style.SUCCESS(
                f'  [完成] {building.name} 房间生成完毕'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'  房间统计: 生成 {total_created}, 跳过 {total_skipped}'
        ))
        return total_created, total_skipped

    def _get_next_equipment_no(self):
        last_eq = Equipment.objects.order_by('-id').first()
        if last_eq and last_eq.equipment_no and last_eq.equipment_no.startswith('EQ'):
            try:
                num = int(last_eq.equipment_no[2:]) + 1
                return f'EQ{num:06d}'
            except ValueError:
                pass
        return 'EQ000001'

    def generate_equipment(self):
        total_created = 0
        total_skipped = 0
        next_no = self._get_next_equipment_no()

        type_cache = {}
        for et in EquipmentType.objects.all():
            type_cache[et.type_name] = et
        # Map equipment names to EquipmentType using type_name from EQUIPMENT_PARAMS
        for eq_name, params in EQUIPMENT_PARAMS.items():
            type_name = params.get('type_name')
            if type_name in type_cache:
                type_cache[eq_name] = type_cache[type_name]

        buildings = Building.objects.select_related('campus').all()
        for building in buildings:
            building_created = 0
            building_skipped = 0
            floors = Floor.objects.filter(building=building).order_by('floor_number')

            for floor in floors:
                rooms = list(Room.objects.filter(floor=floor).order_by('sort', 'id'))

                if building.name in EXCLUDED_BUILDINGS:
                    if rooms:
                        for eq_name, eq_qty in CAFETERIA_FLOOR_EQUIPMENT:
                            existing = Equipment.objects.filter(
                                room=rooms[0], equipment_name=eq_name
                            ).count()
                            need = eq_qty - existing
                            for _ in range(max(0, need)):
                                try:
                                    Equipment.objects.create(
                                        equipment_no=next_no,
                                        equipment_name=eq_name,
                                        equipment_type=type_cache.get(eq_name),
                                        specification=EQUIPMENT_PARAMS.get(eq_name, {}).get('specification', ''),
                                        supplier=EQUIPMENT_PARAMS.get(eq_name, {}).get('supplier', ''),
                                        status='正常', room=rooms[0],
                                    )
                                    total_created += 1
                                    building_created += 1
                                    next_no = self._increment_no(next_no)
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f'  [错误] {str(e)}'))
                            if need <= 0 and eq_qty > 0:
                                total_skipped += eq_qty
                                building_skipped += eq_qty
                    continue

                for idx, room in enumerate(rooms, 1):
                    eq_list = self._get_room_equipment_list(building, idx)
                    for eq_name, eq_qty in eq_list:
                        existing = Equipment.objects.filter(
                            room=room, equipment_name=eq_name
                        ).count()
                        need = eq_qty - existing
                        for _ in range(max(0, need)):
                            try:
                                Equipment.objects.create(
                                    equipment_no=next_no,
                                    equipment_name=eq_name,
                                    equipment_type=type_cache.get(eq_name),
                                    specification=EQUIPMENT_PARAMS.get(eq_name, {}).get('specification', ''),
                                    supplier=EQUIPMENT_PARAMS.get(eq_name, {}).get('supplier', ''),
                                    status='正常', room=room,
                                )
                                total_created += 1
                                building_created += 1
                                next_no = self._increment_no(next_no)
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'  [错误] {str(e)}'))
                        if need <= 0 and eq_qty > 0:
                            total_skipped += eq_qty
                            building_skipped += eq_qty

            if building.name not in FULL_EQUIPMENT_BUILDINGS and building.name not in LIBRARY_BUILDINGS and building.name not in EXCLUDED_BUILDINGS:
                floor_count = floors.count()
                expected_monitors = floor_count * 2
                existing_monitors = Equipment.objects.filter(
                    equipment_name='监控',
                    room__isnull=True,
                    specification=EQUIPMENT_PARAMS.get('监控', {}).get('specification', ''),
                ).count()
                monitors_to_create = max(0, expected_monitors - existing_monitors)
                for _ in range(monitors_to_create):
                    try:
                        Equipment.objects.create(
                            equipment_no=next_no,
                            equipment_name='监控',
                            equipment_type=type_cache.get('监控'),
                            specification=EQUIPMENT_PARAMS.get('监控', {}).get('specification', ''),
                            supplier=EQUIPMENT_PARAMS.get('监控', {}).get('supplier', ''),
                            status='正常', room=None,
                        )
                        total_created += 1
                        building_created += 1
                        next_no = self._increment_no(next_no)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  [错误] {str(e)}'))
                if monitors_to_create <= 0:
                    total_skipped += expected_monitors

            self.stdout.write(self.style.SUCCESS(
                f'  [完成] {building.name} 共生成 {building_created} 台设备'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'  设备统计: 生成 {total_created}, 跳过 {total_skipped}'
        ))
        return total_created, total_skipped

    def _get_room_equipment_list(self, building, room_index):
        if building.name in FULL_EQUIPMENT_BUILDINGS:
            eq_list = list(FULL_ROOM_EQUIPMENT)
            if room_index % 5 == 1:
                eq_list.append(PRINTER_RULE)
            return eq_list
        elif building.name in LIBRARY_BUILDINGS:
            eq_list = list(FULL_ROOM_EQUIPMENT_NO_HOST)
            if room_index % 5 == 1:
                eq_list.append(PRINTER_RULE)
            return eq_list
        else:
            return SIMPLE_ROOM_EQUIPMENT

    def _increment_no(self, current_no):
        num = int(current_no[2:]) + 1
        return f'EQ{num:06d}'
