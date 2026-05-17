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

    return {
        'portal_dashboard_url': f'library:{url_name}',
        'portal_dashboard_url_name': url_name,
        'can_manage_authors': getattr(request.user, 'is_admin', False),
    }
