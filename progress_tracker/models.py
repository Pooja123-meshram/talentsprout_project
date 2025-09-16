from django.db import models
from signUp.models import CustomUser

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('terminated', 'Terminated'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_projects')
    project_name = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    stages = models.TextField(default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    project_costing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for project costing

    def get_stages(self):
        return self.stages.split(',')

    def get_cost_per_stage(self):
        stages = self.get_stages()
        num_stages = len(stages)
        if num_stages == 0 or self.project_costing is None:
            return 0
        return self.project_costing / num_stages

    def __str__(self):
        return f"{self.project_name} (Client: {self.client.username})" if self.client else self.project_name

class Progress(models.Model):
    ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
    ]
    
    project = models.ForeignKey(Project, related_name='progresses', on_delete=models.CASCADE)
    stage = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    status = models.CharField(max_length=255, blank=True, null=True)  # Optional status field
    client_confirmation = models.BooleanField(default=False)  # New field for client confirmation

    def __str__(self):
        return f'{self.project.project_name} - {self.stage} ({self.role})'




class ProjectDetails(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    candidate_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    recruiter = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assigned_projects',
        limit_choices_to={'role': 'recruiter'}  # optional: enforce recruiter role
    )
    candidate = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_projects',
        limit_choices_to={'role': 'candidate'}  # optional: enforce candidate role
    )
    
    project_name = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='project_docs/', null=True, blank=True)
    remarks = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project: {self.project_name} for {self.candidate.username} by {self.recruiter.username}"



# models.py

class ProgressStage(models.Model):
    project_detail = models.ForeignKey(ProjectDetails, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    confirmed_by_recruiter = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    proof_file = models.FileField(upload_to='stage_proofs/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {'Completed' if self.is_completed else 'Pending'}"
