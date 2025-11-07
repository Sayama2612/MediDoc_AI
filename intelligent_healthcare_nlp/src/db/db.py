"""Simple MongoDB helper. If MONGO_URI not provided, raises on get_db()."""
import os

MONGO_URI = os.environ.get('MONGO_URI', '')

_client = None
_db = None


def get_db(db_name='ihn'):
    global _client, _db
    if _db is not None:
        return _db
    if not MONGO_URI:
        raise RuntimeError('MONGO_URI not set. Set environment variable to use DB features.')
    from pymongo import MongoClient
    _client = MongoClient(MONGO_URI)
    _db = _client[db_name]
    # Ensure text index on documents collection for simple search
    try:
        _db['documents'].create_index([('text', 'text')])
    except Exception:
        pass
    return _db
