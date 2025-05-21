from django.forms import ModelForm
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'  #gets all the fields in the models
        exclude = ['host', 'participants']
        