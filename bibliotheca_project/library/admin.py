from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html
from .models import User, Book, Author, Category, Borrowing, Reservation, Penalty, Reclamation


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'user_type', 'is_active_member', 'is_staff', 'is_active')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for User model"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active_member', 'membership_date')
    list_filter = ('user_type', 'is_active_member', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Informations de contact', {'fields': ('phone', 'address')}),
        ('Permissions', {'fields': ('user_type', 'is_active_member', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'membership_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'user_type', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    readonly_fields = ('membership_date',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin configuration for Author model"""
    list_display = ('last_name', 'first_name', 'nationality', 'birth_date')
    list_filter = ('nationality',)
    search_fields = ('last_name', 'first_name')
    ordering = ('last_name', 'first_name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model"""
    list_display = ('title', 'isbn', 'get_authors', 'category', 'total_copies', 'available_copies', 'language')
    list_filter = ('category', 'language', 'publication_date')
    search_fields = ('title', 'isbn', 'publisher')
    filter_horizontal = ('authors',)
    ordering = ('title',)
    
    def get_authors(self, obj):
        return ", ".join([author.__str__() for author in obj.authors.all()])
    get_authors.short_description = 'Auteurs'


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    """Admin configuration for Borrowing model"""
    list_display = ('user', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'penalty_amount')
    list_filter = ('status', 'borrow_date', 'due_date')
    search_fields = ('user__username', 'book__title')
    ordering = ('-borrow_date',)
    
    fieldsets = (
        ('Informations d\'emprunt', {
            'fields': ('user', 'book', 'borrow_date', 'due_date', 'return_date')
        }),
        ('Statut et pénalités', {
            'fields': ('status', 'penalty_amount', 'penalty_paid', 'notes')
        }),
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin configuration for Reservation model"""
    list_display = ('user', 'book', 'reservation_date', 'is_active', 'notification_sent')
    list_filter = ('is_active', 'notification_sent', 'reservation_date')
    search_fields = ('user__username', 'book__title')
    ordering = ('-reservation_date',)


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    """Admin configuration for Penalty model"""
    list_display = ('user', 'borrowing', 'amount', 'status', 'created_date', 'paid_date')
    list_filter = ('status', 'created_date', 'paid_date')
    search_fields = ('user__username', 'borrowing__book__title')
    ordering = ('-created_date',)
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        """Mark selected penalties as paid"""
        updated = queryset.filter(status='pending').update(status='paid')
        self.message_user(request, f'{updated} pénalités marquées comme payées.')
    mark_as_paid.short_description = 'Marquer les pénalités sélectionnées comme payées'


@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    """Admin configuration for Reclamation model"""
    list_display = ('user', 'subject', 'priority', 'status', 'created_date', 'resolved_date')
    list_filter = ('status', 'priority', 'created_date')
    search_fields = ('user__username', 'subject', 'message', 'admin_response')
    ordering = ('-created_date',)
    readonly_fields = ('created_date', 'updated_date', 'resolved_date')
