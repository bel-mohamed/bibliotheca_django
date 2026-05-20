from django.contrib import admin
from django.utils.html import format_html
from .models import Book, Author, Category, Borrowing, Reservation, Penalty, Reclamation


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
        updated = 0
        for penalty in queryset.filter(status='pending'):
            penalty.mark_as_paid()
            updated += 1
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
