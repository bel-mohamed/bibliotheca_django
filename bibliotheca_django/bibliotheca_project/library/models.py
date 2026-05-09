from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Extended User model for library members and librarians
    """
    USER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('librarian', 'Librarian'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='member')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_date = models.DateField(auto_now_add=True)
    is_active_member = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_librarian(self):
        return self.user_type == 'librarian'
    
    @property
    def is_member(self):
        return self.user_type == 'member'


class Category(models.Model):
    """
    Book category model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Author(models.Model):
    """
    Author model
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name_plural = "Authors"


class Book(models.Model):
    """
    Book model with all necessary fields
    """
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    isbn = models.CharField(max_length=13, unique=True, help_text="13-character ISBN")
    publisher = models.CharField(max_length=100)
    publication_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    description = models.TextField(blank=True, null=True)
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='French')
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.isbn})"
    
    @property
    def is_available(self):
        return self.available_copies > 0
    
    @property
    def borrowed_copies(self):
        return self.total_copies - self.available_copies
    
    class Meta:
        ordering = ['-added_date']

class Borrowing(models.Model):
    """
    Borrowing model to track book loans
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    penalty_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    penalty_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"
    
    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return date.today() > self.due_date
    
    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    def calculate_penalty(self):
        """
        Calculate penalty based on days overdue
        Penalty rate: 0.50€ per day overdue
        """
        if self.is_overdue:
            penalty_rate = 0.50  # 0.50€ per day
            self.penalty_amount = self.days_overdue * penalty_rate
            if self.days_overdue > 0:
                self.status = 'overdue'
        else:
            self.penalty_amount = 0.00
        return self.penalty_amount
    
    def return_book(self):
        """
        Mark book as returned and update availability
        """
        if self.status != 'returned':
            self.return_date = models.timezone.now()
            self.status = 'returned'
            self.calculate_penalty()
            self.book.available_copies += 1
            self.book.save()
            self.save()
    
    class Meta:
        ordering = ['-borrow_date']
        unique_together = ['user', 'book', 'borrow_date']


class Reservation(models.Model):
    """
    Reservation model for books that are currently borrowed
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notification_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
    class Meta:
        unique_together = ['user', 'book', 'reservation_date']
        ordering = ['-reservation_date']


class Penalty(models.Model):
    """
    Penalty model for tracking and managing penalties
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='penalties')
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='penalties')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_date = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount}€ ({self.status})"
    
    def mark_as_paid(self, payment_method=None):
        """
        Mark penalty as paid
        """
        self.status = 'paid'
        self.paid_date = models.timezone.now()
        if payment_method:
            self.payment_method = payment_method
        self.borrowing.penalty_paid = True
        self.borrowing.save()
        self.save()
    
    class Meta:
        ordering = ['-created_date']
