from django import forms
from django.forms import inlineformset_factory
from admin_customization.models import HeroSection, WorkStep, ContactInfo, Footer, FooterPortfolioImage,WhyChooseUs



class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = ['heading', 'sub_heading', 'description', 'button_text', 'button_url', 'image1', 'image2', 'image3',
            # Feature fields
            'feature1_icon', 'feature1_title', 'feature1_desc',
            'feature2_icon', 'feature2_title', 'feature2_desc',
            'feature3_icon', 'feature3_title', 'feature3_desc',]
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_heading': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'button_text': forms.TextInput(attrs={'class': 'form-control'}),
            'button_url': forms.URLInput(attrs={'class': 'form-control'}),
            'image1': forms.FileInput(attrs={'class': 'form-control'}),
            'image2': forms.FileInput(attrs={'class': 'form-control'}),
            'image3': forms.FileInput(attrs={'class': 'form-control'}),
             # Feature fields
            'feature1_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'feature1_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature1_desc': forms.TextInput(attrs={'class': 'form-control'}),
            'feature2_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'feature2_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature2_desc': forms.TextInput(attrs={'class': 'form-control'}),
            'feature3_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'feature3_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature3_desc': forms.TextInput(attrs={'class': 'form-control'}),
        }


class WhyChooseUsForm(forms.ModelForm):
    class Meta:
        model = WhyChooseUs
        fields = [
            'heading', 'sub_heading',
            'point1_icon', 'point1_title', 'point1_desc',
            'point2_icon', 'point2_title', 'point2_desc',
            'point3_icon', 'point3_title', 'point3_desc',
            'point4_icon', 'point4_title', 'point4_desc',
            'point5_icon', 'point5_title', 'point5_desc',
            'point6_icon', 'point6_title', 'point6_desc',
        ]
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_heading': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point1_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point1_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point1_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point2_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point2_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point2_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point3_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point3_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point3_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point4_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point4_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point4_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point5_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point5_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point5_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point6_icon': forms.TextInput(attrs={'class': 'form-control'}),
            'point6_title': forms.TextInput(attrs={'class': 'form-control'}),
            'point6_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class WorkStepForm(forms.ModelForm):
    class Meta:
        model = WorkStep
        fields = ['title', 'description', 'icon']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),  # For icon class input (like 'fa-solid fa-sign-in-alt')
        }

class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['name', 'phone', 'email', 'address', 'description', 'button_text', 'contact_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'button_text': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}), 
        }


class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = ['company_name', 'copyright_text', 'quick_links', 'social_links', 'address', 'phone', 'email']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'copyright_text': forms.TextInput(attrs={'class': 'form-control'}),
            'quick_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # JSON data as text
            'social_links': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # JSON data as text
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        

class FooterPortfolioImageForm(forms.ModelForm):
    class Meta:
        model = FooterPortfolioImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Inline formset for FooterPortfolioImage
FooterPortfolioImageFormSet = inlineformset_factory(
    Footer,
    FooterPortfolioImage,
    form=FooterPortfolioImageForm,
    extra=1,  # Number of empty forms to display by default
    can_delete=True,  # Allow deletion of portfolio images
)        