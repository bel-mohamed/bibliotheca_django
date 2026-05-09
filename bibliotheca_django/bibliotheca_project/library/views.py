from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import date, timedelta
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

# ⭐ Déclaration du modèle User personnalisé
User = get_user_model()
from .models import User, Book, Author, Category, Borrowing, Reservation, Penalty
from .forms import (
    UserRegistrationForm, UserLoginForm, BookForm, AuthorForm, 
    CategoryForm, BorrowingForm, UserEditForm, SearchForm
)


def is_librarian(user):
    """Check if user is a librarian"""
    return user.is_authenticated and user.is_librarian


def is_member(user):
    """Check if user is a member"""
    return user.is_authenticated and user.is_member


# ==================== AUTHENTICATION VIEWS ====================

def home(request):
    """Home page view"""
    return render(request, 'library/home.html')


def user_login(request):
    """Login view for both users and librarians"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Bienvenue, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = UserLoginForm()
    
    return render(request, 'library/login.html', {'form': form})
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        
        if password == password2:
            if not User.objects.filter(username=username).exists():
                # Création d'un membre (user_type='member' par défaut)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    phone=phone
                )
                messages.success(request, "Compte créé avec succès !")
                return redirect('login')
            else:
                messages.error(request, "Ce nom d'utilisateur existe déjà")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas")
    
    return render(request, 'register.html')
def user_logout(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard view - redirects based on user type"""
    if request.user.is_librarian:
        return redirect('librarian_dashboard')
    else:
        return redirect('member_dashboard')


# ==================== LIBRARIAN VIEWS ====================

@login_required
@user_passes_test(is_librarian)
def librarian_dashboard(request):
    """Librarian dashboard with statistics"""
    context = {
        'total_books': Book.objects.count(),
        'total_members': User.objects.filter(user_type='member').count(),
        'active_borrowings': Borrowing.objects.filter(status='active').count(),
        'overdue_borrowings': Borrowing.objects.filter(status='overdue').count(),
        'total_penalties': Penalty.objects.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or 0,
        'recent_borrowings': Borrowing.objects.order_by('-borrow_date')[:10],
        'popular_books': Book.objects.annotate(
            borrow_count=Count('borrowings')).order_by('-borrow_count')[:5],
    }
    return render(request, 'library/librarian/dashboard.html', context)


# ==================== BOOK MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def book_list(request):
    """List all books"""
    books = Book.objects.all().order_by('title')
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/librarian/book_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_librarian)
def book_add(request):
    """Add a new book"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Livre "{book.title}" ajouté avec succès!')
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'library/librarian/book_form.html', {'form': form, 'title': 'Ajouter un livre'})


@login_required
@user_passes_test(is_librarian)
def book_edit(request, pk):
    """Edit an existing book"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Livre "{book.title}" modifié avec succès!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'library/librarian/book_form.html', {'form': form, 'title': 'Modifier un livre'})


@login_required
@user_passes_test(is_librarian)
def book_delete(request, pk):
    """Delete a book"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Livre "{title}" supprimé avec succès!')
        return redirect('book_list')
    
    return render(request, 'library/librarian/book_delete.html', {'book': book})


@login_required
@user_passes_test(is_librarian)
def book_detail(request, pk):
    """View book details"""
    book = get_object_or_404(Book, pk=pk)
    borrowings = Borrowing.objects.filter(book=book).order_by('-borrow_date')
    
    return render(request, 'library/librarian/book_detail.html', {
        'book': book,
        'borrowings': borrowings
    })


# ==================== AUTHOR MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def author_list(request):
    """List all authors"""
    authors = Author.objects.all().order_by('last_name')
    paginator = Paginator(authors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/librarian/author_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_librarian)
def author_add(request):
    """Add a new author"""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Auteur "{author}" ajouté avec succès!')
            return redirect('author_list')
    else:
        form = AuthorForm()
    
    return render(request, 'library/librarian/author_form.html', {'form': form, 'title': 'Ajouter un auteur'})


@login_required
@user_passes_test(is_librarian)
def author_edit(request, pk):
    """Edit an existing author"""
    author = get_object_or_404(Author, pk=pk)
    
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Auteur "{author}" modifié avec succès!')
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
    
    return render(request, 'library/librarian/author_form.html', {'form': form, 'title': 'Modifier un auteur'})


@login_required
@user_passes_test(is_librarian)
def author_delete(request, pk):
    """Delete an author"""
    author = get_object_or_404(Author, pk=pk)
    
    if request.method == 'POST':
        name = str(author)
        author.delete()
        messages.success(request, f'Auteur "{name}" supprimé avec succès!')
        return redirect('author_list')
    
    return render(request, 'library/librarian/author_delete.html', {'author': author})


# ==================== CATEGORY MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def category_list(request):
    """List all categories"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'library/librarian/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_librarian)
def category_add(request):
    """Add a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Catégorie "{category.name}" ajoutée avec succès!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'library/librarian/category_form.html', {'form': form, 'title': 'Ajouter une catégorie'})


@login_required
@user_passes_test(is_librarian)
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Catégorie "{category.name}" modifiée avec succès!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'library/librarian/category_form.html', {'form': form, 'title': 'Modifier une catégorie'})


@login_required
@user_passes_test(is_librarian)
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Catégorie "{name}" supprimée avec succès!')
        return redirect('category_list')
    
    return render(request, 'library/librarian/category_delete.html', {'category': category})


# ==================== USER MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def user_list(request):
    """List all users (members and librarians)"""
    users = User.objects.all().order_by('username')
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/librarian/user_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_librarian)
def user_add(request):
    """Add a new user (member or librarian)"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Utilisateur "{user.username}" ajouté avec succès!')
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'library/librarian/user_form.html', {'form': form, 'title': 'Ajouter un utilisateur'})


@login_required
@user_passes_test(is_librarian)
def user_edit(request, pk):
    """Edit an existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Utilisateur "{user.username}" modifié avec succès!')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'library/librarian/user_form.html', {'form': form, 'title': 'Modifier un utilisateur'})


@login_required
@user_passes_test(is_librarian)
def user_delete(request, pk):
    """Delete a user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur "{username}" supprimé avec succès!')
        return redirect('user_list')
    
    return render(request, 'library/librarian/user_delete.html', {'user': user})


@login_required
@user_passes_test(is_librarian)
def user_detail(request, pk):
    """View user details and borrowing history"""
    user = get_object_or_404(User, pk=pk)
    borrowings = Borrowing.objects.filter(user=user).order_by('-borrow_date')
    penalties = Penalty.objects.filter(user=user).order_by('-created_date')
    
    context = {
        'user_profile': user,
        'borrowings': borrowings,
        'penalties': penalties,
    }
    return render(request, 'library/librarian/user_detail.html', context)


# ==================== BORROWING MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def borrowing_list(request):
    """List all borrowings"""
    borrowings = Borrowing.objects.all().order_by('-borrow_date')
    paginator = Paginator(borrowings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/librarian/borrowing_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_librarian)
def borrowing_create(request):
    """Create a new borrowing"""
    if request.method == 'POST':
        form = BorrowingForm(request.POST)
        if form.is_valid():
            borrowing = form.save(commit=False)
            
            # Check if book is available
            if borrowing.book.available_copies <= 0:
                messages.error(request, f'Le livre "{borrowing.book.title}" n\'est pas disponible.')
                return render(request, 'library/librarian/borrowing_form.html', {'form': form})
            
            # Check user borrowing limit
            active_borrowings = Borrowing.objects.filter(
                user=borrowing.user, 
                status__in=['active', 'overdue']
            ).count()
            if active_borrowings >= 5:  # Max 5 borrowings per user
                messages.error(request, f'L\'utilisateur "{borrowing.user.username}" a atteint la limite d\'emprunts.')
                return render(request, 'library/librarian/borrowing_form.html', {'form': form})
            
            # Set due date (14 days from now)
            borrowing.due_date = date.today() + timedelta(days=14)
            borrowing.save()
            
            # Update book availability
            borrowing.book.available_copies -= 1
            borrowing.book.save()
            
            messages.success(request, f'Emprunt créé avec succès pour "{borrowing.book.title}"!')
            return redirect('borrowing_list')
    else:
        form = BorrowingForm()
    
    return render(request, 'library/librarian/borrowing_form.html', {'form': form, 'title': 'Créer un emprunt'})


@login_required
@user_passes_test(is_librarian)
def borrowing_return(request, pk):
    """Return a borrowed book"""
    borrowing = get_object_or_404(Borrowing, pk=pk)
    
    if request.method == 'POST':
        borrowing.return_book()
        messages.success(request, f'Livre "{borrowing.book.title}" retourné avec succès!')
        
        if borrowing.penalty_amount > 0:
            messages.warning(request, f'Une pénalité de {borrowing.penalty_amount}€ a été appliquée.')
        
        return redirect('borrowing_list')
    
    return render(request, 'library/librarian/borrowing_return.html', {'borrowing': borrowing})


@login_required
@user_passes_test(is_librarian)
def borrowing_detail(request, pk):
    """View borrowing details"""
    borrowing = get_object_or_404(Borrowing, pk=pk)
    
    return render(request, 'library/librarian/borrowing_detail.html', {'borrowing': borrowing})


# ==================== PENALTY MANAGEMENT (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def penalty_list(request):
    """List all penalties"""
    penalties = Penalty.objects.all().order_by('-created_date')
    paginator = Paginator(penalties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/librarian/penalty_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_librarian)
def penalty_mark_paid(request, pk):
    """Mark a penalty as paid"""
    penalty = get_object_or_404(Penalty, pk=pk)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cash')
        penalty.mark_as_paid(payment_method)
        messages.success(request, f'Pénalité de {penalty.amount}€ marquée comme payée!')
        return redirect('penalty_list')
    
    return render(request, 'library/librarian/penalty_mark_paid.html', {'penalty': penalty})


# ==================== REPORTS (LIBRARIAN) ====================

@login_required
@user_passes_test(is_librarian)
def report_overdue_books(request):
    """Report of overdue books"""
    overdue_borrowings = Borrowing.objects.filter(status='overdue').order_by('due_date')
    
    return render(request, 'library/librarian/report_overdue.html', {'overdue_borrowings': overdue_borrowings})


@login_required
@user_passes_test(is_librarian)
def report_popular_books(request):
    """Report of most popular books"""
    popular_books = Book.objects.annotate(
        borrow_count=Count('borrowings')
    ).order_by('-borrow_count')[:20]
    
    return render(request, 'library/librarian/report_popular.html', {'popular_books': popular_books})


@login_required
@user_passes_test(is_librarian)
def report_active_members(request):
    """Report of most active members"""
    active_members = User.objects.filter(
        user_type='member'
    ).annotate(
        borrow_count=Count('borrowings')
    ).order_by('-borrow_count')[:20]
    
    return render(request, 'library/librarian/report_active_members.html', {'active_members': active_members})


# ==================== MEMBER VIEWS ====================

@login_required
@user_passes_test(is_member)
def member_dashboard(request):
    """Member dashboard with personal information"""
    user = request.user
    active_borrowings = Borrowing.objects.filter(
        user=user, 
        status__in=['active', 'overdue']
    )
    overdue_borrowings = active_borrowings.filter(status='overdue')
    pending_penalties = Penalty.objects.filter(user=user, status='pending')
    reservations = Reservation.objects.filter(user=user, is_active=True)
    
    context = {
        'active_borrowings': active_borrowings,
        'overdue_borrowings': overdue_borrowings,
        'pending_penalties': pending_penalties,
        'reservations': reservations,
        'can_borrow': active_borrowings.count() < 5,
    }
    return render(request, 'library/member/dashboard.html', context)


@login_required
@user_passes_test(is_member)
def book_search(request):
    """Search books with performance optimization"""
    form = SearchForm(request.GET or None)
    books = Book.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        author = form.cleaned_data.get('author')
        language = form.cleaned_data.get('language')
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(isbn__icontains=query) |
                Q(description__icontains=query) |
                Q(publisher__icontains=query)
            )
        
        if category:
            books = books.filter(category=category)
        
        if author:
            books = books.filter(authors=author)
        
        if language:
            books = books.filter(language=language)
    
    # Performance optimization: use select_related and prefetch_related
    books = books.select_related('category').prefetch_related('authors').order_by('title')
    
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/member/book_search.html', {
        'form': form,
        'page_obj': page_obj
    })


@login_required
@user_passes_test(is_member)
def book_detail_member(request, pk):
    """View book details for members"""
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    
    # Check if user has already borrowed this book
    active_borrowing = Borrowing.objects.filter(
        user=user, 
        book=book, 
        status__in=['active', 'overdue']
    ).first()
    
    # Check if user has reserved this book
    reservation = Reservation.objects.filter(
        user=user, 
        book=book, 
        is_active=True
    ).first()
    
    context = {
        'book': book,
        'active_borrowing': active_borrowing,
        'reservation': reservation,
        'can_borrow': book.is_available and not active_borrowing and not reservation,
    }
    return render(request, 'library/member/book_detail.html', context)


@login_required
@user_passes_test(is_member)
def my_borrowings(request):
    """View member's borrowing history"""
    borrowings = Borrowing.objects.filter(user=request.user).order_by('-borrow_date')
    paginator = Paginator(borrowings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/member/my_borrowings.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_member)
def borrow_book(request, pk):
    """Borrow a book"""
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    
    if request.method == 'POST':
        # Check if book is available
        if not book.is_available:
            messages.error(request, f'Le livre "{book.title}" n\'est pas disponible.')
            return redirect('book_detail_member', pk=pk)
        
        # Check if user has already borrowed this book
        existing_borrowing = Borrowing.objects.filter(
            user=user, 
            book=book, 
            status__in=['active', 'overdue']
        ).exists()
        
        if existing_borrowing:
            messages.error(request, 'Vous avez déjà emprunté ce livre.')
            return redirect('book_detail_member', pk=pk)
        
        # Check user borrowing limit
        active_borrowings = Borrowing.objects.filter(
            user=user, 
            status__in=['active', 'overdue']
        ).count()
        
        if active_borrowings >= 5:
            messages.error(request, 'Vous avez atteint la limite d\'emprunts (5 livres).')
            return redirect('book_detail_member', pk=pk)
        
        # Create borrowing
        borrowing = Borrowing.objects.create(
            user=user,
            book=book,
            due_date=date.today() + timedelta(days=14)
        )
        
        # Update book availability
        book.available_copies -= 1
        book.save()
        
        messages.success(request, f'Livre "{book.title}" emprunté avec succès! Date de retour: {borrowing.due_date}')
        return redirect('my_borrowings')
    
    return render(request, 'library/member/borrow_book.html', {'book': book})


@login_required
@user_passes_test(is_member)
def return_book(request, pk):
    """Return a borrowed book (member request)"""
    borrowing = get_object_or_404(Borrowing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        borrowing.return_book()
        messages.success(request, f'Livre "{borrowing.book.title}" retourné avec succès!')
        
        if borrowing.penalty_amount > 0:
            messages.warning(request, f'Une pénalité de {borrowing.penalty_amount}€ a été appliquée.')
        
        return redirect('my_borrowings')
    
    return render(request, 'library/member/return_book.html', {'borrowing': borrowing})


@login_required
@user_passes_test(is_member)
def reserve_book(request, pk):
    """Reserve a book that is not available"""
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    
    if request.method == 'POST':
        # Check if book is available
        if book.is_available:
            messages.info(request, f'Le livre "{book.title}" est disponible. Vous pouvez l\'emprunter directement.')
            return redirect('borrow_book', pk=pk)
        
        # Check if user has already reserved this book
        existing_reservation = Reservation.objects.filter(
            user=user, 
            book=book, 
            is_active=True
        ).exists()
        
        if existing_reservation:
            messages.error(request, 'Vous avez déjà réservé ce livre.')
            return redirect('book_detail_member', pk=pk)
        
        # Create reservation
        reservation = Reservation.objects.create(
            user=user,
            book=book
        )
        
        messages.success(request, f'Livre "{book.title}" réservé avec succès! Vous serez notifié dès qu\'il sera disponible.')
        return redirect('my_reservations')
    
    return render(request, 'library/member/reserve_book.html', {'book': book})


@login_required
@user_passes_test(is_member)
def my_reservations(request):
    """View member's reservations"""
    reservations = Reservation.objects.filter(
        user=request.user, 
        is_active=True
    ).order_by('-reservation_date')
    
    return render(request, 'library/member/my_reservations.html', {'reservations': reservations})


@login_required
@user_passes_test(is_member)
def cancel_reservation(request, pk):
    """Cancel a reservation"""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user, is_active=True)
    
    if request.method == 'POST':
        book_title = reservation.book.title
        reservation.is_active = False
        reservation.save()
        messages.info(request, f'Réservation pour "{book_title}" annulée.')
        return redirect('my_reservations')
    
    return render(request, 'library/member/cancel_reservation.html', {'reservation': reservation})


@login_required
@user_passes_test(is_member)
def my_penalties(request):
    """View member's penalties"""
    penalties = Penalty.objects.filter(user=request.user).order_by('-created_date')
    paginator = Paginator(penalties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/member/my_penalties.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_member)
def my_profile(request):
    """View and edit member profile"""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('my_profile')
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'library/member/my_profile.html', {'form': form})
