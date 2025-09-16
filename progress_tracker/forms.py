from django import forms
from .models import Progress, Project ,ProjectDetails,ProgressStage

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['stage', 'is_completed',]
        widgets = {
            'stage': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',  # Make the field read-only
                'style': 'border-radius: 8px; border-color: #ced4da;'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 20px; height: 20px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stage'].label = 'Stage Name'
        self.fields['is_completed'].label = 'Completed'
        self.fields['is_completed'].required = False  # Optional: make the checkbox optional

class StatusForm(forms.ModelForm):
    terminate = forms.BooleanField(required=True, label='Terminate Project')

    class Meta:
        model = Project
        fields = ['status', 'terminate']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px; border-color: #ced4da;'
            }),
            'terminate': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 20px; height: 20px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = 'Project Status'




class ProjectDetailsForm(forms.ModelForm):
    class Meta:
        model = ProjectDetails
        fields = ['project_name', 'description', 'tech_stack', 'document', 'remarks']



class ProgressStageForm(forms.ModelForm):
    class Meta:
        model = ProgressStage
        fields = ['title', 'description',]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stage Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe this stage'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Stage Title',
            'description': 'Details',
            'is_completed': 'Mark as Completed',
        }

class StageCompletionForm(forms.ModelForm):
    class Meta:
        model = ProgressStage
        fields = ['proof_file']
