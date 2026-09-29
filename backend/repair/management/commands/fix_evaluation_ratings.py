from django.core.management.base import BaseCommand
from repair.models import Evaluation

class Command(BaseCommand):
    help = '修复评价数据的综合评分'
    
    def handle(self, *args, **options):
        evaluations = Evaluation.objects.all()
        fixed_count = 0
        
        for eval in evaluations:
            avg = (eval.quality_rating + eval.speed_rating + eval.attitude_rating) / 3
            correct_rating = round(avg)
            
            if eval.rating != correct_rating:
                eval.rating = correct_rating
                eval.save(update_fields=['rating'])
                fixed_count += 1
                self.stdout.write(f'修复评价 {eval.repair_no}: {eval.rating} -> {correct_rating}')
        
        self.stdout.write(self.style.SUCCESS(f'\n修复完成! 共修复 {fixed_count} 条评价数据'))
