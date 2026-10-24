import datetime
from django.conf import settings

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False


def log_payment_event_to_mongo(event_type, transaction_id, student_id, amount, status, details=None):
    """
    Logs payment transaction events directly to MongoDB collection 'payment_audit_logs'.
    These documents can be viewed natively in MongoDB Compass.
    """
    if not MONGO_AVAILABLE:
        return False

    try:
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client[settings.MONGO_DB_NAME]
        collection = db['payment_audit_logs']

        document = {
            'event_type': event_type,
            'transaction_id': str(transaction_id),
            'student_id': student_id,
            'amount': float(amount),
            'status': status,
            'details': details or {},
            'timestamp': datetime.datetime.now(datetime.timezone.utc),
            'environment': 'DEMO_PROTOTYPE_DIT'
        }

        collection.insert_one(document)
        return True
    except Exception as e:
        # Graceful fallback if MongoDB service is offline
        print(f"[Mongo Audit Logger Warning] Failed to log event to MongoDB: {e}")
        return False
