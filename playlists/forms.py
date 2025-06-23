from django import forms
from .models import Poll, Song

class PollForm(forms.ModelForm):
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select songs for the poll (minimum 5, maximum 20)"
    )
    
    class Meta:
        model = Poll
        fields = ['title', 'start_time', 'end_time', 'songs']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_songs(self):
        songs = self.cleaned_data['songs']
        if len(songs) < 5:
            raise forms.ValidationError("You must select at least 5 songs for the poll.")
        if len(songs) > 20:
            raise forms.ValidationError("You can select at most 20 songs for the poll.")
        return songs
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data

class SongSelectionForm(forms.Form):
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select songs to add to the playlist"
    )