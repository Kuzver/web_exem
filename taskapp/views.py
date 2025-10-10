from datetime import datetime
import calendar
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Task, Project, TaskMakerUser, ProjectMember
from .forms import RegisterForm, ProjectForm, TaskForm
from .serializers import TaskSerializer, ProjectSerializer

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .forms import ProjectForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Task
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import FieldError
from .models import Task
from datetime import datetime

from django.http import JsonResponse
from .models import Task  # Import the Task model
from datetime import datetime
from django.core.exceptions import FieldError

from datetime import datetime


# В представлении
from django.shortcuts import render
from .models import Task

from django.http import JsonResponse
from datetime import datetime
from .models import Task

from django.http import JsonResponse
from datetime import datetime
from .models import Task

from django.http import JsonResponse

from django.http import JsonResponse
from .models import Task  # Убедитесь, что импортируете модель Task
from django.http import JsonResponse
from .models import Task

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Task
from django.http import JsonResponse
from datetime import date
import calendar
from .models import Task
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import date
import calendar
from .models import Task
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import ProjectMember, Project
from django.contrib.auth import get_user_model
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .models import Task
from rest_framework.permissions import BasePermission
from .models import ProjectMember
from rest_framework import permissions
from django.core.exceptions import PermissionDenied

User = get_user_model()
@require_POST
@login_required
def add_project_member(request):
    user_id = request.POST.get('user_id')
    project_id = request.POST.get('project_id')
    project_role = request.POST.get('project_role')

    try:
        user = User.objects.get(id=user_id)
        project = Project.objects.get(id=project_id)
        # Добавить проверку, что request.user — админ проекта
        if not ProjectMember.objects.filter(user=request.user, project=project, project_role='Администратор').exists():
            return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)

        pm, created = ProjectMember.objects.get_or_create(user=user, project=project,
                                                          defaults={'project_role': project_role})
        if not created:
            pm.project_role = project_role
            pm.save()
        return JsonResponse({'status': 'success', 'created': created})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)

@login_required
def api_tasks_by_month(request):
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        project_id = request.GET.get('project_id')
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid year or month'}, status=400)

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    tasks = Task.objects.filter(task_should_done_date__range=(start_date, end_date))

    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        # Проверяем роль пользователя в проекте
        is_admin = ProjectMember.objects.filter(
            project=project,
            user=request.user,
            project_role='Администратор'
        ).exists()

        if is_admin:
            tasks = tasks.filter(project=project)
        else:
            tasks = tasks.filter(project=project, task_implementer=request.user)
    else:
        # Если проект не указан, показываем личные задачи пользователя
        tasks = tasks.filter(creator=request.user, task_mode='Личный')

    data = [task.to_dict() for task in tasks]
    return JsonResponse(data, safe=False)


@login_required
def task_list_json(request):
    project_id = request.GET.get('project_id')
    tasks = Task.objects.all()

    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        is_admin = ProjectMember.objects.filter(
            project=project,
            user=request.user,
            project_role='Администратор'
        ).exists()

        if is_admin:
            tasks = tasks.filter(project=project)
        else:
            tasks = tasks.filter(project=project, task_implementer=request.user)

    else:
        tasks = tasks.filter(creator=request.user, task_mode='Личный')

    data = [task.to_dict() for task in tasks]
    return JsonResponse(data, safe=False)



# Вход пользователя

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('task_list')  # 🔁 Перенаправление после успешного входа
        else:
            return render(request, 'taskapp/home.html', {'error_message': 'Неверное имя пользователя или пароль.'})
    return redirect('home')

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list', user_id=request.user.id)
    else:
        form = RegisterForm()
    return render(request, 'taskapp/register.html', {'form': form})

# Главная страница
def home(request):
    user = request.user
    projects_with_counts = []

    if user.is_authenticated:
        projects = ProjectMember.objects.filter(user=user).select_related('project')
        for pm in projects:
            project = pm.project
            members_count = ProjectMember.objects.filter(project=project).count()
            projects_with_counts.append({
                'project': project,
                'members_count': members_count,
            })

    return render(request, 'taskapp/home.html', {
        'projects_with_counts': projects_with_counts
    })


# Список задач
@login_required
def task_list(request, user_id=None):
    if user_id:
        try:
            user_id = int(user_id)
            tasks = Task.objects.filter(creator__id=user_id)
        except ValueError:
            tasks = Task.objects.filter(creator=request.user)
    else:
        tasks = Task.objects.filter(creator=request.user)

    return render(request, 'taskapp/task_list.html', {'tasks': tasks})


# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

@api_view(['GET'])
def api_tasks_by_user(request, user_id):
    tasks = Task.objects.filter(creator__id=user_id)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


import json


import datetime
from django.utils import timezone

import datetime
from django.utils import timezone

from datetime import datetime
import logging
logger = logging.getLogger(__name__)



# Ajax список задач по календарю
from django.db.models import Q
from calendar import Calendar
from django.http import JsonResponse
from datetime import date
from .models import Task, Project, ProjectMember

@login_required
def task_list_ajax(request):
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        project_id = request.GET.get("project_id")
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    cal = Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    calendar_data = []

    # Определяем дату начала и конца месяца
    start_date = date(year, month, 1)
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # Получаем задачи за месяц
    tasks = Task.objects.filter(task_should_done_date__range=(start_date, end_date))

    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        is_admin = ProjectMember.objects.filter(
            project=project,
            user=request.user,
            project_role__iexact='Администратор'
        ).exists()

        if is_admin:
            tasks = tasks.filter(project=project)
        else:
            tasks = tasks.filter(
                project=project
            ).filter(
                Q(task_implementer=request.user) | Q(creator=request.user)
            )
    else:
        tasks = tasks.filter(creator=request.user, task_mode='Личный')

    # Формируем данные по дням
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'tasks': []})
            else:
                day_tasks = tasks.filter(task_should_done_date__day=day)
                week_data.append({
                    'day': day,
                    'tasks': list(day_tasks.values('id', 'task_name', 'task_priority'))
                })
        calendar_data.append(week_data)

    return JsonResponse({'calendar_data': calendar_data})


# Календарь задач
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from calendar import monthrange
import calendar
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import Task, Project
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def calendar_view(request):
    current_date = timezone.now()
    month = int(request.GET.get('month', current_date.month))
    year = int(request.GET.get('year', current_date.year))
    _, num_days = monthrange(year, month)

    project_id = request.GET.get('project_id')
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = None

    # Фильтруем задачи по месяцу, году и проекту, если он есть
    tasks = Task.objects.filter(
        task_should_done_date__month=month,
        task_should_done_date__year=year
    )
    if project:
        tasks = tasks.filter(project=project)

    days = {day: [] for day in range(1, num_days + 1)}
    for task in tasks:
        days[task.task_should_done_date.day].append(task)

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Получаем пользователей — участников проекта, если проект задан, иначе всех
    if project:
        users = project.members.all()
    else:
        users = User.objects.none()  # Или User.objects.all(), если хотите всех

    users_json = json.dumps(
        list(users.values('id', 'username')),
        cls=DjangoJSONEncoder
    )

    return render(request, 'calendar.html', {
        'users_json': users_json,
        'is_admin': request.user.is_staff,
        'user': request.user,
        'project': project,
        'days': days,
        'months': months,
        'month': month,
        'year': year,
    })


# Командная работа
from django.contrib.auth.decorators import login_required

@login_required
def team_work(request, project_id):
    user = request.user

    project = get_object_or_404(Project, id=project_id)
    # Проверка, что пользователь участник проекта
    if not ProjectMember.objects.filter(project=project, user=user).exists():
        messages.error(request, "Нет доступа к этому проекту.")
        return redirect('home')

    members = ProjectMember.objects.filter(project=project).select_related('user')
    tasks = Task.objects.filter(project=project)

    return render(request, 'taskapp/team_work.html', {
        'project': project,
        'members': members,
        'tasks': tasks,
    })



# Создание проекта
@login_required
def create_team(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()

            ProjectMember.objects.get_or_create(
                user=request.user,
                project=project,
                defaults={'project_role': 'admin'}
            )

            members = form.cleaned_data.get('members')
            if members:
                for user in members:
                    if user != request.user:
                        ProjectMember.objects.get_or_create(
                            user=user,
                            project=project,
                            defaults={'project_role': 'participant'}
                        )

            messages.success(request, 'Проект успешно создан!')

            # Передаем id проекта в team_work
            return redirect('team_work', project_id=project.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ProjectForm()
    return render(request, 'taskapp/create_team.html', {'form': form})

# Назначение задачи проекту
@login_required
def assign_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    users = TaskMakerUser.objects.all()
    task_form = TaskForm(request.POST or None)

    if request.method == 'POST' and task_form.is_valid():
        task = task_form.save(commit=False)
        task.project = project
        task.save()
        return redirect('team_work')

    return render(request, 'taskapp/team_work.html', {
        'form': task_form,
        'project': project,
        'users': users,
        'errors': task_form.errors if task_form.errors else None
    })

# Управление проектом
@login_required
def manage_project(request, project_id=None):
    project = get_object_or_404(Project, id=project_id) if project_id else None
    tasks = Task.objects.filter(project=project) if project else []
    users = TaskMakerUser.objects.all()

    if request.method == 'POST':
        if 'create_project' in request.POST:
            project_form = ProjectForm(request.POST)
            if project_form.is_valid():
                project = project_form.save()
                return redirect('manage_project', project_id=project.id)

        elif 'create_task' in request.POST and project:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.save()
                return redirect('manage_project', project_id=project.id)

        elif 'assign_implementer' in request.POST and project:
            task_id = request.POST.get('task_id')
            implementer_id = request.POST.get('task_implementer')
            task = get_object_or_404(Task, id=task_id)
            implementer = get_object_or_404(TaskMakerUser, id=implementer_id)
            task.task_implementer = implementer
            task.save()
            return redirect('manage_project', project_id=project.id)

    return render(request, 'taskapp/team_work.html', {
        'project_form': ProjectForm(),
        'task_form': TaskForm(),
        'tasks': tasks,
        'project': project,
        'users': users,
    })


# API - задачи по пользователю и проекту
class TaskSummaryView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        project_id = request.query_params.get('project_id')

        if not user_id or not project_id:
            return Response({"error": "Параметры user_id и project_id обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        tasks = Task.objects.filter(creator_id=user_id, project_id=project_id)
        tasks_data = [{'task_name': task.task_name, 'task_date': task.task_date} for task in tasks]
        return Response({"tasks": tasks_data})

# DRF ViewSet - задачи
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        user = self.request.user
        project_id = self.request.data.get('project_id')

        if not project_id:
            raise ValidationError("Параметр project_id обязателен")

        # Проверка: является ли пользователь админом проекта
        is_admin = ProjectMember.objects.filter(
            project_id=project_id,
            user=user,
            project_role='Администратор'
        ).exists()

        if not is_admin:
            raise PermissionDenied("Только администратор может создавать задачи")

        serializer.save(creator=user, project_id=project_id)

    def get_queryset(self):
        user = self.request.user
        # Получаем проекты, где пользователь участник
        user_projects = ProjectMember.objects.filter(user=user).values_list('project', flat=True)

        # Для администратора проекта — все задачи проекта,
        # Для исполнителя — только свои задачи
        # Предполагаем, что в ProjectMember есть поле project_role
        admin_projects = ProjectMember.objects.filter(user=user, project_role='Администратор').values_list('project',
                                                                                                           flat=True)

        # Возвращаем задачи:
        # Если пользователь — администратор проекта, видит все задачи проекта
        # Иначе — только свои задачи в проектах, где он участник
        if admin_projects:
            return Task.objects.filter(project__in=admin_projects)
        else:
            return Task.objects.filter(project__in=user_projects, task_implementer=user)


# DRF API - список проектов
class ProjectListCreateView(ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        project_id = self.request.query_params.get('project_id')
        queryset = Project.objects.all()
        if user_id:
            queryset = queryset.filter(projectmember__user_id=user_id)
        if project_id:
            queryset = queryset.filter(id=project_id)
        return queryset

class TaskAPIView(APIView):
    def get(self, request):
        date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        project_id = request.GET.get('project_id')

        tasks = Task.objects.all()
        if date:
            tasks = tasks.filter(task_make_date=date)
        if user_id:
            tasks = tasks.filter(creator_id=user_id)
        if project_id and project_id != '-1':
            tasks = tasks.filter(project_id=project_id)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({"error": "project_id обязателен"}, status=400)

        is_admin = ProjectMember.objects.filter(
            project_id=project_id,
            user=request.user,
            project_role='Администратор'
        ).exists()

        if not is_admin:
            return Response({"error": "Только администратор может создавать задачи"}, status=403)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@require_http_methods(["GET"])
@login_required
def api_task_list(request):
    date = request.GET.get('date')
    user_id = request.GET.get('user_id')
    project_id = request.GET.get('project_id')

    tasks = Task.objects.all()

    if date:
        tasks = tasks.filter(task_should_done_date=date)  # Замените на task_should_done_date
    if user_id:
        tasks = tasks.filter(creator_id=user_id)
    if project_id and project_id != "-1":
        tasks = tasks.filter(project_id=project_id)  # Исправьте фильтрацию по проекту

    data = [{
        'id': task.id,
        'task_name': task.task_name,
        'task_status': task.task_status,
        'task_date': str(task.task_should_done_date),  # Убедитесь, что отправляется task_should_done_date
    } for task in tasks]

    return JsonResponse(data, safe=False)

# Пример: taskapp/views.py
@csrf_exempt
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'PATCH':
        data = json.loads(request.body)

        # Обновление статуса и приоритета
        task_status = data.get('task_status')
        task_priority = data.get('task_priority')

        if task_status in dict(Task.STATUS_CHOICES):
            task.task_status = task_status

        if task_priority in dict(Task.PRIORITY_CHOICES):
            task.task_priority = task_priority

        task.save()

        return JsonResponse({'success': True, 'task': task.to_dict()})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def project_calendar_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, projectmember__user=request.user)

    tasks = Task.objects.filter(project=project)
    members = ProjectMember.objects.filter(project=project).select_related('user')

    return render(request, 'taskapp/team_work.html', {
        'project': project,
        'tasks': tasks,
        'members': members,
    })

@require_http_methods(["GET"])
@login_required
def api_task_list(request):
    date = request.GET.get('date')
    user_id = request.GET.get('user_id')
    project_id = request.GET.get('project_id')

    tasks = Task.objects.all()

    if date:
        tasks = tasks.filter(task_should_done_date=date)  # Замените на task_should_done_date
    if user_id:
        tasks = tasks.filter(creator_id=user_id)
    if project_id and project_id != "-1":
        tasks = tasks.filter(project_id=project_id)  # Исправьте фильтрацию по проекту

    data = [{
        'id': task.id,
        'task_name': task.task_name,
        'task_status': task.task_status,
        'task_date': str(task.task_should_done_date),  # Убедитесь, что отправляется task_should_done_date
    } for task in tasks]

    return JsonResponse(data, safe=False)

class IsProjectAdmin(BasePermission):
    def has_permission(self, request, view):
        project_id = request.data.get('project_id') or request.query_params.get('project_id')
        if not project_id:
            return False
        try:
            membership = ProjectMember.objects.get(project_id=project_id, user=request.user)
        except ProjectMember.DoesNotExist:
            return False
        return membership.role == 'admin'

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, но редактирование только админам проекта.
    """
    def has_permission(self, request, view):
        return True  # доступ к списку/созданию проверяется в has_object_permission

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True  # GET, HEAD — всегда разрешены
        # только если пользователь — админ проекта задачи
        return obj.project.is_admin(request.user)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, TaskMakerUser, Project
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@csrf_exempt  # лучше потом убрать и использовать CSRF-токен на фронте
@login_required
def add_task(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    task_name = data.get('task_name')
    if not task_name:
        return JsonResponse({'error': 'Название задачи обязательно'}, status=400)

    task_description = data.get('task_description', '')
    task_should_done_date_str = data.get('task_should_done_date')
    task_priority = data.get('task_priority', 'Средний')
    task_status = data.get('task_status', 'Новая')
    project_id = data.get('project_id')
    assignee_id = data.get('assignee_id')

    from .models import TaskMakerUser, Project, Task

    # Преобразуем дату из строки в объект date
    task_should_done_date = None
    if task_should_done_date_str:
        try:
            task_should_done_date = datetime.strptime(task_should_done_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Неверный формат даты. Ожидается YYYY-MM-DD'}, status=400)

    assignee = TaskMakerUser.objects.filter(id=assignee_id).first() if assignee_id else None

    project = None
    if project_id:
        project = Project.objects.filter(id=project_id).first()
        if not project:
            return JsonResponse({'error': 'Проект не найден'}, status=404)

    task = Task.objects.create(
        creator=request.user,
        task_name=task_name,
        task_description=task_description,
        task_should_done_date=task_should_done_date,
        task_priority=task_priority,
        task_status=task_status,
        project=project,
        assignee=assignee,
        task_implementer=assignee if assignee else request.user,
        task_mode='Командный' if project else 'Личный'
    )

    return JsonResponse({
        'success': True,
        'task': {
            'id': task.id,
            'task_name': task.task_name,
            'task_description': task.task_description,
            'task_should_done_date': task_should_done_date_str if task_should_done_date_str else None,
            'task_priority': task.task_priority,
            'task_status': task.task_status,
            'project_id': project.id if project else None,
            'assignee_id': assignee.id if assignee else None,
            'task_implementer_id': task.task_implementer.id,
            'task_mode': task.task_mode,
        }
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ProjectMember

@login_required
def project_users(request):
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'project_id parameter is required'}, status=400)

    # Проверка, что пользователь входит в проект (безопасность)
    if not ProjectMember.objects.filter(project_id=project_id, user=request.user).exists():
        return JsonResponse({'error': 'Access denied'}, status=403)

    members = ProjectMember.objects.filter(project_id=project_id).select_related('user')
    users_data = [{
        'id': member.user.id,
        'username': member.user.user_login,
        'project_role': member.project_role,
    } for member in members]

    return JsonResponse(users_data, safe=False)
