from .models import Reservation, Reclamation

def portal_dashboard(request):
    """URL du tableau de bord selon le type d'utilisateur connecté."""
    if not request.user.is_authenticated:
        return {}

    if getattr(request.user, 'is_admin', False):
        url_name = 'admin_dashboard'
    elif getattr(request.user, 'is_librarian', False):
        url_name = 'librarian_dashboard'
    else:
        url_name = 'member_dashboard'

    reservation_notification_count = 0
    reclamation_notification_count = 0
    if getattr(request.user, 'is_member', False):
        reservation_notification_count = Reservation.objects.filter(
            user=request.user,
            is_active=True,
            notification_sent=True
        ).count()

        reclamation_notification_count = Reclamation.objects.filter(
            user=request.user,
            status='resolved',
            admin_response__isnull=False,
            response_read=False
        ).count()

    return {
        'portal_dashboard_url': f'library:{url_name}',
        'portal_dashboard_url_name': url_name,
        'can_manage_authors': getattr(request.user, 'is_admin', False),
        'reservation_notification_count': reservation_notification_count,
        'reclamation_notification_count': reclamation_notification_count,
    }
