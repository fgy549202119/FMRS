from django.db import models


class Campus(models.Model):
    name = models.CharField('院区名称', max_length=50)
    code = models.CharField('院区编码', max_length=20, unique=True)
    description = models.TextField('描述', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        db_table = 'campus'
        verbose_name = '院区'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Building(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='buildings', verbose_name='所属院区')
    name = models.CharField('楼栋名称', max_length=100)
    code = models.CharField('楼栋编码', max_length=50, unique=True)

    class Meta:
        db_table = 'building'
        verbose_name = '楼栋'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f'{self.campus.name}-{self.name}'


class Floor(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='floors', verbose_name='所属院区', null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors', verbose_name='所属楼栋')
    floor_number = models.IntegerField('楼层号')

    class Meta:
        db_table = 'floor'
        verbose_name = '楼层'
        verbose_name_plural = verbose_name
        ordering = ['building__id', 'floor_number']
        unique_together = [['building', 'floor_number']]

    def __str__(self):
        return f'{self.building.name}{self.floor_number}层'


class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms', verbose_name='所属楼层')
    name = models.CharField('房间名称', max_length=100)
    sort = models.IntegerField('排序号', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'room'
        verbose_name = '房间'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']
        unique_together = [['floor', 'name']]

    def __str__(self):
        return f'{self.floor.building.name}{self.floor.floor_number}层{self.name}'
