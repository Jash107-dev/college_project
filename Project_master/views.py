from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project
from .forms import ProjectForm

def project_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if request.user.is_authenticated:
        if request.user.is_staff:
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(student=request.user)
    else:
        projects = Project.objects.all()  # anonymous users see all projects
    
    if query:
        projects = projects.filter(Q(title__icontains=query))
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    paginator = Paginator(projects.order_by('-created_at'), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'Project_master/project_list.html', context)

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'Project_master/project_form.html', {'form': form, 'action': 'Create'})

def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.student != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'Project_master/project_form.html', {'form': form, 'action': 'Update'})

def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.student != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('project_list')
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'Project_master/project_confirm_delete.html', {'project': project})
