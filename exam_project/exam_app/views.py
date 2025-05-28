from django.shortcuts import render

from django.shortcuts import render
from .models import ipexam

def ipexam_list(request):
    exams = ipexam.objects.filter(is_public=True)
    return render(request, 'exam_app/ipexam_list.html', {'exams': exams})
