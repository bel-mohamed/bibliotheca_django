from django.urls import path
from . import views

app_name = 'library'



app_name = 'library'

urlpatterns = [
    # ==================== ADMIN URLS ====================
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

      
    # ==================== LIBRARIAN URLS ====================
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    
    # Book Management
    path('librarian/books/', views.book_list, name='book_list'),
    path('librarian/books/add/', views.book_add, name='book_add'),
    path('librarian/books/<int:pk>/', views.book_detail, name='book_detail'),
    path('librarian/books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('librarian/books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # Author Management
    path('librarian/authors/', views.author_list, name='author_list'),
    path('librarian/authors/add/', views.author_add, name='author_add'),
    path('librarian/authors/<int:pk>/edit/', views.author_edit, name='author_edit'),
    path('librarian/authors/<int:pk>/delete/', views.author_delete, name='author_delete'),
    
    # Category Management
    path('librarian/categories/', views.category_list, name='category_list'),
    path('librarian/categories/add/', views.category_add, name='category_add'),
    path('librarian/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('librarian/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # User Management
    path('librarian/users/', views.user_list, name='user_list'),
    path('librarian/users/add/', views.user_add, name='user_add'),
    path('librarian/users/<int:pk>/', views.user_detail, name='user_detail'),
    path('librarian/users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('librarian/users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Borrowing Management
    path('librarian/borrowings/', views.borrowing_list, name='borrowing_list'),
    path('librarian/borrowings/add/', views.borrowing_create, name='borrowing_create'),
    path('librarian/borrowings/<int:pk>/', views.borrowing_detail, name='borrowing_detail'),
    path('librarian/borrowings/<int:pk>/return/', views.borrowing_return, name='borrowing_return'),
    
    # Penalty Management
    path('librarian/penalties/', views.penalty_list, name='penalty_list'),
    path('librarian/penalties/<int:pk>/mark-paid/', views.penalty_mark_paid, name='penalty_mark_paid'),
    
    # Reports
    path('librarian/reports/overdue/', views.report_overdue_books, name='report_overdue'),
    path('librarian/reports/popular/', views.report_popular_books, name='report_popular'),
    path('librarian/reports/active-members/', views.report_active_members, name='report_active_members'),
    
    # Reclamations
    path('librarian/reclamations/', views.reclamation_list, name='reclamation_list'),
    path('librarian/reclamations/<int:pk>/', views.reclamation_detail, name='reclamation_detail'),
    
    # ==================== MEMBER URLS ====================
    path('member/', views.member_dashboard, name='member_dashboard'),
    
    # Book Search and Details
    path('books/search/', views.book_search, name='book_search'),
    path('books/<int:pk>/', views.book_detail_member, name='book_detail_member'),
    
    # Borrowing Actions
    path('books/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
    path('borrowings/<int:pk>/return/', views.return_book, name='return_book_member'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    
    # Reservations
    path('books/<int:pk>/reserve/', views.reserve_book, name='reserve_book'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    
    # Penalties
    path('my-penalties/', views.my_penalties, name='my_penalties'),
    
    # Profile
    path('profile/', views.my_profile, name='my_profile'),
    
    # Reclamations
    path('reclamations/create/', views.create_reclamation, name='create_reclamation'),
    path('my-reclamations/', views.my_reclamations, name='my_reclamations'),
]
