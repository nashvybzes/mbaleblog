from django import forms
from .models import Subscriber, Comment, Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 5}),
        }
        labels = {
            'name': 'Your Name',
            'email': 'Email Address',
            'subject': 'Subject',
            'message': 'Your Message',
        }

class CommentForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)  
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['username', 'text', 'parent_id', 'honeypot']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'text': forms.Textarea(attrs={'placeholder': 'Write your comment...'}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your email...',
                'class': 'newsletter-input'
            })
        }
