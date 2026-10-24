from accounts.models import Notification

def notifications_processor(request):
    """Global context processor rendering unread notifications for authenticated users."""
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user)
        unread_count = user_notifications.filter(is_read=False).count()
        recent_notifications = user_notifications[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
