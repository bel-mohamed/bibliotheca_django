from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch

from .models import Book, Author, Category, Borrowing, Reservation, Penalty

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '0123456789',
            'address': '123 Test Street'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'member')
        self.assertTrue(user.is_member)
        self.assertFalse(user.is_librarian)
    
    def test_create_librarian(self):
        """Test creating a librarian user"""
        user_data = self.user_data.copy()
        user_data['user_type'] = 'librarian'
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.user_type, 'librarian')
        self.assertTrue(user.is_librarian)
        self.assertFalse(user.is_member)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.username} ({user.get_user_type_display()})"
        self.assertEqual(str(user), expected)


class AuthorModelTest(TestCase):
    """Test cases for Author model"""
    
    def setUp(self):
        self.author_data = {
            'first_name': 'Victor',
            'last_name': 'Hugo',
            'birth_date': date(1802, 2, 26),
            'nationality': 'Française'
        }
    
    def test_create_author(self):
        """Test creating an author"""
        author = Author.objects.create(**self.author_data)
        self.assertEqual(author.first_name, 'Victor')
        self.assertEqual(author.last_name, 'Hugo')
        self.assertEqual(str(author), 'Victor Hugo')
    
    def test_author_str_representation(self):
        """Test author string representation"""
        author = Author.objects.create(**self.author_data)
        self.assertEqual(str(author), 'Victor Hugo')


class CategoryModelTest(TestCase):
    """Test cases for Category model"""
    
    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Roman',
            description='Livres de fiction'
        )
        self.assertEqual(category.name, 'Roman')
        self.assertEqual(str(category), 'Roman')


class BookModelTest(TestCase):
    """Test cases for Book model"""
    
    def setUp(self):
        self.author = Author.objects.create(
            first_name='J.K.',
            last_name='Rowling'
        )
        self.category = Category.objects.create(name='Fantasy')
        self.book_data = {
            'title': 'Harry Potter',
            'isbn': '978-0747532699',
            'publisher': 'Bloomsbury',
            'publication_date': date(1997, 6, 26),
            'category': self.category,
            'description': 'A wizard story',
            'pages': 223,
            'language': 'English',
            'total_copies': 5,
            'available_copies': 5
        }
    
    def test_create_book(self):
        """Test creating a book"""
        book = Book.objects.create(**self.book_data)
        book.authors.add(self.author)
        self.assertEqual(book.title, 'Harry Potter')
        self.assertTrue(book.is_available)
        self.assertEqual(book.borrowed_copies, 0)
    
    def test_book_str_representation(self):
        """Test book string representation"""
        book = Book.objects.create(**self.book_data)
        expected = f"{book.title} ({book.isbn})"
        self.assertEqual(str(book), expected)
    
    def test_book_availability(self):
        """Test book availability logic"""
        book = Book.objects.create(**self.book_data)
        self.assertTrue(book.is_available)
        
        book.available_copies = 0
        book.save()
        self.assertFalse(book.is_available)


class BorrowingModelTest(TestCase):
    """Test cases for Borrowing model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author'
        )
        self.category = Category.objects.create(name='Test Category')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publisher='Test Publisher',
            publication_date=date(2020, 1, 1),
            category=self.category,
            pages=200,
            language='French',
            total_copies=3,
            available_copies=3
        )
        self.book.authors.add(self.author)
    
    def test_create_borrowing(self):
        """Test creating a borrowing"""
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.status, 'active')
    
    def test_borrowing_overdue_calculation(self):
        """Test overdue calculation"""
        # Create borrowing with past due date
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() - timedelta(days=5)
        )
        self.assertTrue(borrowing.is_overdue)
        self.assertEqual(borrowing.days_overdue, 5)
    
    def test_penalty_calculation(self):
        """Test penalty calculation"""
        # Create overdue borrowing
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() - timedelta(days=3)
        )
        penalty = borrowing.calculate_penalty()
        expected_penalty = 3 * 0.50  # 3 days * 0.50€ per day
        self.assertEqual(float(penalty), expected_penalty)
    
    def test_return_book(self):
        """Test returning a book"""
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        initial_available = self.book.available_copies
        
        borrowing.return_book()
        
        self.assertEqual(borrowing.status, 'returned')
        self.assertEqual(self.book.available_copies, initial_available + 1)


class ViewTest(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.librarian = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='libpass123',
            user_type='librarian'
        )
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author'
        )
        self.category = Category.objects.create(name='Test Category')
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publisher='Test Publisher',
            publication_date=date(2020, 1, 1),
            category=self.category,
            pages=200,
            language='French',
            total_copies=3,
            available_copies=3
        )
        self.book.authors.add(self.author)
    
    def test_home_view(self):
        """Test home page view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bibliothèque')
    
    def test_login_view_get(self):
        """Test login page GET request"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')
    
    def test_login_view_post_valid(self):
        """Test login with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_login_view_post_invalid(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nom d\'utilisateur ou mot de passe incorrect')
    
    def test_register_view_get(self):
        """Test registration page GET request"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer un compte')
    
    def test_register_view_post_valid(self):
        """Test registration with valid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_logout_view(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
    
    def test_member_dashboard_requires_login(self):
        """Test that member dashboard requires login"""
        response = self.client.get(reverse('member_dashboard'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("member_dashboard")}')
    
    def test_member_dashboard_authenticated(self):
        """Test member dashboard for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('member_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tableau de bord')
    
    def test_librarian_dashboard_requires_librarian(self):
        """Test that librarian dashboard requires librarian role"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('librarian_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_librarian_dashboard_authenticated(self):
        """Test librarian dashboard for authenticated librarian"""
        self.client.login(username='librarian', password='libpass123')
        response = self.client.get(reverse('librarian_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tableau de bord - Bibliothécaire')
    
    def test_book_search_view(self):
        """Test book search functionality"""
        response = self.client.get(reverse('book_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rechercher des livres')
    
    def test_book_search_with_query(self):
        """Test book search with query parameter"""
        response = self.client.get(reverse('book_search'), {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
    
    def test_borrow_book_view(self):
        """Test borrowing a book"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('borrow_book', kwargs={'pk': self.book.pk}))
        self.assertRedirects(response, reverse('my_borrowings'))
        
        # Check if borrowing was created
        self.assertTrue(Borrowing.objects.filter(
            user=self.user,
            book=self.book
        ).exists())
        
        # Check if book availability was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)
    
    def test_borrow_book_limit(self):
        """Test borrowing limit (5 books per user)"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create 5 books and borrow them
        books = []
        for i in range(5):
            book = Book.objects.create(
                title=f'Book {i}',
                isbn=f'123456789{i}',
                publisher='Test Publisher',
                publication_date=date(2020, 1, 1),
                category=self.category,
                pages=200,
                language='French',
                total_copies=1,
                available_copies=1
            )
            books.append(book)
            Borrowing.objects.create(
                user=self.user,
                book=book,
                due_date=date.today() + timedelta(days=14)
            )
        
        # Try to borrow a 6th book
        response = self.client.post(reverse('borrow_book', kwargs={'pk': self.book.pk}))
        self.assertContains(response, 'Vous avez atteint la limite d\'emprunts')


class PerformanceTest(TestCase):
    """Test cases for performance requirements"""
    
    def setUp(self):
        # Create test data for performance testing
        self.author = Author.objects.create(
            first_name='Performance',
            last_name='Test'
        )
        self.category = Category.objects.create(name='Performance Test')
        
        # Create 100 books for testing
        self.books = []
        for i in range(100):
            book = Book.objects.create(
                title=f'Performance Book {i}',
                isbn=f'123456789{i:02d}',
                publisher='Test Publisher',
                publication_date=date(2020, 1, 1),
                category=self.category,
                pages=200,
                language='French',
                total_copies=3,
                available_copies=3
            )
            book.authors.add(self.author)
            self.books.append(book)
    
    def test_search_performance(self):
        """Test that book search returns results in under 2 seconds"""
        from django.test.utils import override_settings
        import time
        
        with override_settings(DEBUG=True):
            start_time = time.time()
            response = self.client.get(reverse('book_search'), {'query': 'Performance'})
            end_time = time.time()
            
            response_time = end_time - start_time
            self.assertLess(response_time, 2.0, "Search should return results in under 2 seconds")
            self.assertEqual(response.status_code, 200)


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.librarian = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='libpass123',
            user_type='librarian'
        )
        self.author = Author.objects.create(
            first_name='Integration',
            last_name='Test'
        )
        self.category = Category.objects.create(name='Integration Test')
    
    def test_complete_borrowing_workflow(self):
        """Test complete borrowing workflow"""
        # Create a book as librarian
        self.client.login(username='librarian', password='libpass123')
        book = Book.objects.create(
            title='Integration Test Book',
            isbn='9876543210',
            publisher='Test Publisher',
            publication_date=date(2020, 1, 1),
            category=self.category,
            pages=200,
            language='French',
            total_copies=1,
            available_copies=1
        )
        book.authors.add(self.author)
        
        # Logout librarian and login as member
        self.client.logout()
        self.client.login(username='testuser', password='testpass123')
        
        # Search for the book
        response = self.client.get(reverse('book_search'), {'query': 'Integration'})
        self.assertContains(response, 'Integration Test Book')
        
        # Borrow the book
        response = self.client.post(reverse('borrow_book', kwargs={'pk': book.pk}))
        self.assertRedirects(response, reverse('my_borrowings'))
        
        # Check borrowing was created
        borrowing = Borrowing.objects.get(user=self.user, book=book)
        self.assertEqual(borrowing.status, 'active')
        
        # Return the book
        response = self.client.post(reverse('return_book_member', kwargs={'pk': borrowing.pk}))
        self.assertRedirects(response, reverse('my_borrowings'))
        
        # Check book was returned
        borrowing.refresh_from_db()
        self.assertEqual(borrowing.status, 'returned')
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 1)
