# library/models.py
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator

# Délai d'emprunt démo (30 secondes) et tarif par période de retard
BORROWING_DUE_SECONDS = 30
PENALTY_RATE_PER_PERIOD = Decimal('0.50')

# ========== MODÈLES PRINCIPAUX ==========

class User(AbstractUser):
    """
    Extended User model for library members and librarians
    """
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='member')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_date = models.DateField(auto_now_add=True)
    is_active_member = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
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
    Author model - UNE SEULE DÉFINITION
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name_plural = "Authors"
        ordering = ['last_name', 'first_name']


class Book(models.Model):
    """
    Book model - UNE SEULE DÉFINITION avec ManyToMany vers Author
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
    
    def get_authors_names(self):
        """Retourne les noms des auteurs"""
        return ", ".join([author.__str__() for author in self.authors.all()])

    def save(self, *args, **kwargs):
        old_available = None
        if self.pk:
            try:
                old_book = Book.objects.get(pk=self.pk)
                old_available = old_book.available_copies
            except Book.DoesNotExist:
                old_available = None

        super().save(*args, **kwargs)

        if old_available is not None and old_available <= 0 and self.available_copies > 0:
            notify_reservations_for_book(self)
    
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
    due_date = models.DateTimeField()
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
        return timezone.now() > self.due_date

    @property
    def seconds_overdue(self):
        if not self.is_overdue:
            return 0
        return int((timezone.now() - self.due_date).total_seconds())

    @property
    def days_overdue(self):
        """Nombre de périodes de 30 secondes en retard."""
        if not self.is_overdue:
            return 0
        return max(1, (self.seconds_overdue + BORROWING_DUE_SECONDS - 1) // BORROWING_DUE_SECONDS)

    def calculate_penalty(self):
        """Calcule la pénalité : 0,50 € par période de 30 secondes de retard."""
        if self.is_overdue:
            self.penalty_amount = self.days_overdue * PENALTY_RATE_PER_PERIOD
            self.status = 'overdue'
        else:
            self.penalty_amount = Decimal('0.00')
        return self.penalty_amount

    def ensure_penalty_record(self):
        """Crée ou met à jour l'enregistrement Penalty lié à cet emprunt."""
        if self.penalty_amount <= 0:
            return None
        penalty, created = Penalty.objects.get_or_create(
            borrowing=self,
            defaults={
                'user': self.user,
                'amount': self.penalty_amount,
                'status': 'pending',
            },
        )
        if not created and penalty.status == 'pending':
            penalty.amount = self.penalty_amount
            penalty.user = self.user
            penalty.save(update_fields=['amount', 'user'])
        return penalty

    def return_book(self):
        """
        Mark book as returned and update availability
        """
        if self.status != 'returned':
            self.return_date = timezone.now()
            self.calculate_penalty()
            self.status = 'returned'
            self.ensure_penalty_record()
            self.book.available_copies += 1
            self.book.save()
            self.save()
    
    class Meta:
        ordering = ['-borrow_date']


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

    def mark_as_paid(self, payment_method='cash'):
        """Mark this penalty as paid and record payment metadata."""
        self.status = 'paid'
        self.paid_date = timezone.now()
        self.payment_method = payment_method
        self.save(update_fields=['status', 'paid_date', 'payment_method'])


def notify_reservations_for_book(book):
    """Send a notification email to active reservations when a book becomes available."""
    if book.available_copies <= 0:
        return 0

    sent_count = 0
    reservations = book.reservations.filter(is_active=True, notification_sent=False).select_related('user')
    subject = f'Votre réservation est disponible : {book.title}'

    for reservation in reservations:
        recipient = reservation.user.email
        if not recipient:
            continue

        message = (
            f'Bonjour {reservation.user.get_full_name() or reservation.user.username},\n\n'
            f'Le livre réservé "{book.title}" est maintenant disponible. '
            'Vous avez 48 heures pour venir l\'emprunter.\n\n'
            'Merci de vous connecter à votre espace bibliothèque pour finaliser l\'emprunt.\n\n'
            'Cordialement,\nL\'équipe de la bibliothèque'
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@bibliotheque.local')
        send_mail(subject, message, from_email, [recipient], fail_silently=True)

        reservation.notification_sent = True
        reservation.save(update_fields=['notification_sent'])
        sent_count += 1

    return sent_count


class Reclamation(models.Model):
    """
    Reclamation model for students to send messages to admin
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('rejected', 'Rejeté'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reclamations')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    admin_response = models.TextField(blank=True, null=True)
    response_read = models.BooleanField(default=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.status})"
    
    def mark_as_resolved(self, response=None):
        """
        Mark reclamation as resolved
        """
        self.status = 'resolved'
        self.resolved_date = timezone.now()
        self.response_read = False
        if response:
            self.admin_response = response
            self.send_response_notification()
        self.save()

    def send_response_notification(self):
        """Send a notification email to the user when the admin replies."""
        recipient = self.user.email
        if not recipient:
            return

        subject = f'Réponse à votre réclamation : {self.subject}'
        message = (
            f'Bonjour {self.user.get_full_name() or self.user.username},\n\n'
            'Votre réclamation a reçu une réponse de l\'administration.\n\n'
            f'Sujet : {self.subject}\n\n'
            'Réponse :\n'
            f'{self.admin_response}\n\n'
            'Connectez-vous à votre espace bibliothèque pour voir les détails.\n\n'
            'Cordialement,\nL\'équipe de la bibliothèque'
        )

        send_mail(
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@bibliotheque.local'),
            [recipient],
            fail_silently=True
        )
    
    def mark_as_in_progress(self):
        """
        Mark reclamation as in progress
        """
        self.status = 'in_progress'
        self.save()
    
    class Meta:
        ordering = ['-created_date']