from decimal import Decimal

from django.db.models import Q, Sum

from .models import Borrowing, Penalty


def get_penalty_totals(user):
    """Calcule les totaux de pénalités pour un étudiant."""
    penalties = Penalty.objects.filter(user=user)
    totals = penalties.aggregate(
        total_all=Sum('amount'),
        total_pending=Sum('amount', filter=Q(status='pending')),
        total_paid=Sum('amount', filter=Q(status='paid')),
    )
    return {
        'total_all': totals['total_all'] or Decimal('0.00'),
        'total_pending': totals['total_pending'] or Decimal('0.00'),
        'total_paid': totals['total_paid'] or Decimal('0.00'),
        'count_pending': penalties.filter(status='pending').count(),
        'count_paid': penalties.filter(status='paid').count(),
    }


def sync_penalties():
    """Synchronise les pénalités pour tous les emprunts en retard."""
    for borrowing in Borrowing.objects.filter(status__in=['active', 'overdue']).select_related('user', 'book'):
        if borrowing.is_overdue:
            borrowing.calculate_penalty()
            borrowing.save(update_fields=['penalty_amount', 'status'])
            borrowing.ensure_penalty_record()
