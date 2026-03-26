from django import forms
from .models import FarmerQuery


class FarmerInputForm(forms.ModelForm):
    """
    Main form for farmers to input their details
    Supports both English and Hindi labels
    """
    
    class Meta:
        model = FarmerQuery
        fields = ['location', 'soil_type', 'season', 'water_availability', 'land_area', 'language']
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Ludhiana, Punjab or लुधियाना, पंजाब',
                'id': 'location-input',
                'autocomplete': 'off'
            }),
            'soil_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'soil-type-select'
            }),
            'season': forms.Select(attrs={
                'class': 'form-select',
                'id': 'season-select'
            }),
            'water_availability': forms.Select(attrs={
                'class': 'form-select',
                'id': 'water-select'
            }),
            'land_area': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 2.5',
                'min': '0.1',
                'max': '1000',
                'step': '0.1',
                'id': 'land-area-input'
            }),
            'language': forms.RadioSelect(attrs={
                'class': 'lang-radio',
                'id': 'language-radio'
            }),
        }
        labels = {
            'location': 'Location / स्थान',
            'soil_type': 'Soil Type / मिट्टी का प्रकार',
            'season': 'Season / ऋतु',
            'water_availability': 'Water Availability / जल उपलब्धता',
            'land_area': 'Land Area in Acres / भूमि क्षेत्र (एकड़)',
            'language': 'Output Language / भाषा',
        }
    
    def clean_location(self):
        location = self.cleaned_data.get('location', '').strip()
        if not location:
            raise forms.ValidationError("Please enter your location / कृपया अपना स्थान दर्ज करें")
        if len(location) < 2:
            raise forms.ValidationError("Location must be at least 2 characters / स्थान कम से कम 2 अक्षरों का होना चाहिए")
        return location
    
    def clean_land_area(self):
        area = self.cleaned_data.get('land_area')
        if area is not None and (area <= 0 or area > 10000):
            raise forms.ValidationError("Land area must be between 0.1 and 10,000 acres")
        return area
