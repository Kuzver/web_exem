from django.shortcuts import render

from django.shortcuts import render
from .models import vkexam

from django.shortcuts import render
from .models import vkexam

def vkexam_list(request):
    exams = vkexam.objects.filter(is_public=True)
    context = {
        'exams': exams,
        'full_name': 'Кузнецова Вера Владиславовна',
        'group_number': 'Группа 241-671',
    }
    return render(request, 'exam_app/vkexam_list.html', context)
