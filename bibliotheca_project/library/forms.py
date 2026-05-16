from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book, Author, Category, Borrowing


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'username': "Nom d'utilisateur",
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'phone': 'Téléphone',
            'address': 'Adresse',
            'password1': 'Mot de passe',
            'password2': 'Confirmation du mot de passe',
        }
        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['rows'] = 3
        self.fields['password1'].help_text = 'Minimum 8 caractères.'
        if self.is_bound and self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    css = self.fields[field_name].widget.attrs.get('class', 'form-control')
                    self.fields[field_name].widget.attrs['class'] = f'{css} is-invalid'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'member'
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Form for user login
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )


class UserEditForm(forms.ModelForm):
    """
    Form for editing user profile
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BookForm(forms.ModelForm):
    """
    Form for adding/editing books
    """
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Book
        fields = ('title', 'authors', 'isbn', 'publisher', 'publication_date', 
                 'category', 'description', 'pages', 'language', 'total_copies', 
                 'available_copies', 'cover_image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['authors'].queryset = Author.objects.all().order_by('last_name', 'first_name')


class AuthorForm(forms.ModelForm):
    """
    Form for adding/editing authors
    """
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'birth_date', 'nationality')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    """
    Form for adding/editing categories
    """
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BorrowingForm(forms.ModelForm):
    """
    Form for creating borrowings (librarian only)
    """
    class Meta:
        model = Borrowing
        fields = ('user', 'book')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show members in user selection
        self.fields['user'].queryset = User.objects.filter(user_type='member').order_by('username')
        # Only show available books in book selection
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0).order_by('title')


class SearchForm(forms.Form):
    """
    Form for searching books
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par titre, ISBN, auteur, éditeur...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        empty_label="Tous les auteurs",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    language = forms.ChoiceField(
        choices=[
            ('', 'Toutes les langues'),
            ('French', 'Français'),
            ('English', 'Anglais'),
            ('Spanish', 'Espagnol'),
            ('German', 'Allemand'),
            ('Italian', 'Italien'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
