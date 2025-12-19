from django import forms
from .models import Venue, VenueImage, Amenity

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def to_python(self, data):
        if not data:
            return None
        # Si data es una lista (varios archivos), no hacemos nada, la dejamos pasar.
        # El FileField normal de Django intentaría validarlo y fallaría.
        if isinstance(data, list):
            return [super(MultipleFileField, self).to_python(f) for f in data]
        return super().to_python(data)

    def clean(self, data, initial=None):
        # Si es una lista, validamos que no esté vacía si es required=True
        if isinstance(data, list) and not data and self.required:
             raise forms.ValidationError(self.error_messages['required'])
        return data

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'description', 'capacity', 'size_sqm', 'price_per_hour', 'latitude', 'longitude', 'amenities', 'ar_model', 'is_active']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'size_sqm': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'ar_model': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Piscina, Wifi 5G...'}),
        }