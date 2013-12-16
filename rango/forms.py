from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length = 128, help_text = "Please enter the category name")
    views = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)
    likes = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)

    class Meta:
        model = Category # link ModelForm to the Model


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length = 128, help_text = "Please enter the title of the page")
    url = forms.URLField(max_length = 200, help_text = "Please enter the page URL")
    views = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # if url doesn't start with "http://", pretend it does
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

    class Meta:
        model = Page

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ('title','url','views')

class UserForm(forms.ModelForm):
    password = forms.CharField(help_text = "Please enter a password.", widget = forms.PasswordInput())
    username = forms.CharField(help_text = "Please enter a user name.")
    email = forms.CharField(help_text = "Please enter your email.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text = "Please enter your website.", required = False)
    picture = forms.ImageField(help_text = "Select an image to upload.", required = False)

    class Meta:
        model = UserProfile
        fields = ['website', 'picture']

