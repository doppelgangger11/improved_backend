from django import forms

from .models import Problems

class ProblemsForm(forms.ModelForm):
    class Meta:
        model = Problems
        exclude = ['status', 'story', 'assigned_user', 'resolved_user']

class ProblemsUpdateStatusForm(forms.ModelForm):
    class Meta:
        model = Problems
        fields = ['status', 'story']

class ProblemEditForm(forms.ModelForm):
    class Meta:
        model = Problems
        fields = ['description', 'status', 'assigned_user', 'resolved_user']
