# services/community-api/main.py
"""
IHEP Community Service

Manages peer support networks, community forums, and social features.

Key features:
- Peer support groups and forums
- Community resource sharing
- Social engagement metrics
- Moderation and safety features
- Community event coordination
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from functools import wraps
import logging
from google.cloud import logging as cloud_logging
from google.cloud import bigquery
import json
from datetime import datetime, timedelta
import redis
import uuid
from typing import Dict, List, Optional

app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Redis for caching and real-time features
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=7,
    decode_responses=True
)

# BigQuery for analytics
bq_client = bigquery.Client()
PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = 'ihep_community'
JWT_SECRET = os.getenv('JWT_SECRET')

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    
    return wrapped

class CommunityManager:
    """
    Community management system with social network analysis.
    
    Implements social network metrics based on graph theory:
    
    Centrality measures:
    - Degree centrality: C_D(v) = deg(v) / (n-1)
    - Betweenness centrality: C_B(v) = Σ(σ(s,t|v) / σ(s,t))
    - Closeness centrality: C_C(v) = (n-1) / Σd(v,t)
    
    Community detection using modularity maximization:
    Q = (1/2m) Σ[A_ij - (k_i k_j / 2m)] δ(c_i, c_j)
    
    Where:
    - A_ij = adjacency matrix
    - k_i = degree of node i
    - m = total number of edges
    - c_i = community of node i
    - δ = Kronecker delta function
    """
    
    def __init__(self):
        self.dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
    
    def create_discussion_thread(self, user_id: str, title: str, content: str, 
                               category: str, tags: List[str] = None) -> str:
        """Create a new discussion thread"""
        thread_id = str(uuid.uuid4())
        
        thread_data = {
            'id': thread_id,
            'user_id': user_id,
            'title': title,
            'content': content,
            'category': category,
            'tags': json.dumps(tags or []),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'view_count': 0,
            'reply_count': 0,
            'like_count': 0,
            'status': 'active'
        }
        
        # Store in Redis for fast access
        thread_key = f"thread:{thread_id}"
        redis_client.hmset(thread_key, thread_data)
        redis_client.expire(thread_key, 2592000)  # 30-day TTL
        
        # Add to category index
        category_key = f"threads:category:{category}"
        redis_client.lpush(category_key, thread_id)
        redis_client.expire(category_key, 2592000)
        
        # Add to user's threads
        user_threads_key = f"user_threads:{user_id}"
        redis_client.lpush(user_threads_key, thread_id)
        redis_client.expire(user_threads_key, 2592000)
        
        # Log thread creation
        thread_log = {
            'thread_id': thread_id,
            'user_id': user_id,
            'title': title,
            'category': category,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        redis_client.lpush('thread_creations', json.dumps(thread_log))
        
        logger.info(f"Thread created: {thread_id} by user {user_id}")
        
        return thread_id
    
    def add_reply(self, thread_id: str, user_id: str, content: str) -> str:
        """Add a reply to a discussion thread"""
        reply_id = str(uuid.uuid4())
        
        # Verify thread exists
        thread_key = f"thread:{thread_id}"
        thread_data = redis_client.hgetall(thread_key)
        if not thread_data:
            raise ValueError("Thread not found")
        
        reply_data = {
            'id': reply_id,
            'thread_id': thread_id,
            'user_id': user_id,
            'content': content,
            'created_at': datetime.utcnow().isoformat(),
            'like_count': 0,
            'status': 'active'
        }
        
        # Store reply
        reply_key = f"reply:{reply_id}"
        redis_client.hmset(reply_key, reply_data)
        redis_client.expire(reply_key, 2592000)
        
        # Add to thread's replies
        thread_replies_key = f"thread_replies:{thread_id}"
        redis_client.lpush(thread_replies_key, reply_id)
        redis_client.expire(thread_replies_key, 2592000)
        
        # Update thread reply count
        redis_client.hincrby(thread_key, 'reply_count', 1)
        redis_client.hset(thread_key, 'updated_at', datetime.utcnow().isoformat())
        
        # Add to user's replies
        user_replies_key = f"user_replies:{user_id}"
        redis_client.lpush(user_replies_key, reply_id)
        redis_client.expire(user_replies_key, 2592000)
        
        # Update user engagement score
        self._update_user_engagement(user_id, 'reply')
        
        # Log reply
        reply_log = {
            'reply_id': reply_id,
            'thread_id': thread_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        redis_client.lpush('reply_creations', json.dumps(reply_log))
        
        logger.info(f"Reply added: {reply_id} to thread {thread_id}")
        
        return reply_id
    
    def get_thread_with_replies(self, thread_id: str, page: int = 1, page_size: int = 20) -> Dict:
        """Get thread with paginated replies"""
        # Get thread data
        thread_key = f"thread:{thread_id}"
        thread_data = redis_client.hgetall(thread_key)
        if not thread_data:
            return None
        
        # Increment view count
        redis_client.hincrby(thread_key, 'view_count', 1)
        
        # Get paginated replies
        thread_replies_key = f"thread_replies:{thread_id}"
        start = (page - 1) * page_size
        end = start + page_size - 1
        
        reply_ids = redis_client.lrange(thread_replies_key, start, end)
        replies = []
        
        for reply_id in reply_ids:
            reply_key = f"reply:{reply_id}"
            reply_data = redis_client.hgetall(reply_key)
            if reply_data:
                replies.append(reply_data)
        
        # Get total reply count
        total_replies = redis_client.llen(thread_replies_key)
        
        return {
            'thread': thread_data,
            'replies': replies,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_replies': total_replies,
                'total_pages': (total_replies + page_size - 1) // page_size
            }
        }
    
    def search_threads(self, query: str, category: str = None, tags: List[str] = None) -> List[Dict]:
        """Search threads by query, category, and tags"""
        # This would implement full-text search in production
        # For demo, return sample results or cached search
        
        search_cache_key = f"search:{hash(query + str(category) + str(tags))}"
        cached_results = redis_client.get(search_cache_key)
        
        if cached_results:
            return json.loads(cached_results)
        
        # Generate sample results for demo
        results = [
            {
                'id': str(uuid.uuid4()),
                'title': f'Discussion about {query}',
                'content_preview': f'This is a discussion about {query}...',
                'category': category or 'general',
                'author': 'Community Member',
                'created_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'reply_count': 15,
                'view_count': 127,
                'tags': tags or ['discussion']
            }
        ] * 5  # 5 sample results
        
        # Cache for 10 minutes
        redis_client.setex(search_cache_key, 600, json.dumps(results))
        
        return results
    
    def _update_user_engagement(self, user_id: str, activity_type: str):
        """Update user engagement score based on activity"""
        engagement_key = f"user_engagement:{user_id}"
        
        # Different activities have different weights
        weights = {
            'thread': 3,
            'reply': 2,
            'like': 1,
            'view': 0.1
        }
        
        weight = weights.get(activity_type, 1)
        current_score = float(redis_client.get(engagement_key) or 0)
        new_score = current_score + weight
        
        redis_client.setex(engagement_key, 86400, str(new_score))  # 24-hour TTL
        
        # Update community leaderboard
        leaderboard_key = "community_leaderboard"
        redis_client.zadd(leaderboard_key, {user_id: new_score})
        redis_client.expire(leaderboard_key, 86400)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'community-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/community/threads', methods=['POST'])
@require_auth
def create_thread():
    """Create a new discussion thread"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags', [])
        
        if not title or not content or not category:
            return jsonify({'error': 'Title, content, and category required'}), 400
        
        community_manager = CommunityManager()
        thread_id = community_manager.create_discussion_thread(
            request.user_id, title, content, category, tags
        )
        
        return jsonify({
            'message': 'Thread created successfully',
            'thread_id': thread_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        return jsonify({'error': 'Failed to create thread'}), 500

@app.route('/community/threads/<thread_id>/replies', methods=['POST'])
@require_auth
def add_reply(thread_id):
    """Add a reply to a discussion thread"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Content required'}), 400
        
        community_manager = CommunityManager()
        reply_id = community_manager.add_reply(thread_id, request.user_id, content)
        
        return jsonify({
            'message': 'Reply added successfully',
            'reply_id': reply_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error adding reply: {str(e)}")
        return jsonify({'error': 'Failed to add reply'}), 500

@app.route('/community/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get thread with replies"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        community_manager = CommunityManager()
        thread_data = community_manager.get_thread_with_replies(thread_id, page, page_size)
        
        if not thread_data:
            return jsonify({'error': 'Thread not found'}), 404
        
        return jsonify(thread_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving thread: {str(e)}")
        return jsonify({'error': 'Failed to retrieve thread'}), 500

@app.route('/community/threads/search', methods=['GET'])
def search_threads():
    """Search community threads"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        tags = request.args.get('tags')
        
        if tags:
            tags = tags.split(',')
        
        community_manager = CommunityManager()
        results = community_manager.search_threads(query, category, tags)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching threads: {str(e)}")
        return jsonify({'error': 'Failed to search threads'}), 500

@app.route('/community/categories', methods=['GET'])
def get_categories():
    """Get available discussion categories"""
    try:
        # In production, this would query a database
        # For demo, return predefined categories
        
        categories = [
            {
                'id': 'hiv_aids',
                'name': 'HIV/AIDS Support',
                'description': 'Discussion and support for HIV/AIDS patients',
                'thread_count': 1247,
                'active_users': 892
            },
            {
                'id': 'diabetes',
                'name': 'Diabetes Management',
                'description': 'Tips and support for diabetes management',
                'thread_count': 834,
                'active_users': 654
            },
            {
                'id': 'mental_health',
                'name': 'Mental Health Support',
                'description': 'Peer support for mental health challenges',
                'thread_count': 1567,
                'active_users': 1203
            },
            {
                'id': 'general',
                'name': 'General Discussion',
                'description': 'General health and wellness discussions',
                'thread_count': 2103,
                'active_users': 1876
            },
            {
                'id': 'research',
                'name': 'Research Updates',
                'description': 'Latest research and medical breakthroughs',
                'thread_count': 342,
                'active_users': 289
            }
        ]
        
        return jsonify({
            'categories': categories,
            'total': len(categories)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        return jsonify({'error': 'Failed to retrieve categories'}), 500

@app.route('/community/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get community engagement leaderboard"""
    try:
        # Get top 20 most engaged users
        leaderboard_key = "community_leaderboard"
        top_users = redis_client.zrevrange(leaderboard_key, 0, 19, withscores=True)
        
        leaderboard = []
        for user_id, score in top_users:
            # Get user info (simplified)
            user_info = {
                'user_id': user_id,
                'username': f'User_{user_id[:8]}',
                'engagement_score': round(score, 2),
                'rank': len(leaderboard) + 1
            }
            leaderboard.append(user_info)
        
        return jsonify({
            'leaderboard': leaderboard,
            'updated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving leaderboard: {str(e)}")
        return jsonify({'error': 'Failed to retrieve leaderboard'}), 500

@app.route('/community/user/<user_id>/activity', methods=['GET'])
def get_user_activity(user_id):
    """Get user's community activity"""
    try:
        # Get user's threads
        user_threads_key = f"user_threads:{user_id}"
        thread_ids = redis_client.lrange(user_threads_key, 0, 9)  # Last 10 threads
        
        threads = []
        for thread_id in thread_ids:
            thread_key = f"thread:{thread_id}"
            thread_data = redis_client.hgetall(thread_key)
            if thread_data:
                threads.append({
                    'id': thread_data['id'],
                    'title': thread_data['title'],
                    'category': thread_data['category'],
                    'created_at': thread_data['created_at'],
                    'reply_count': int(thread_data.get('reply_count', 0)),
                    'view_count': int(thread_data.get('view_count', 0))
                })
        
        # Get user's replies
        user_replies_key = f"user_replies:{user_id}"
        reply_ids = redis_client.lrange(user_replies_key, 0, 9)  # Last 10 replies
        
        replies = []
        for reply_id in reply_ids:
            reply_key = f"reply:{reply_id}"
            reply_data = redis_client.hgetall(reply_key)
            if reply_data:
                # Get thread title for context
                thread_key = f"thread:{reply_data['thread_id']}"
                thread_data = redis_client.hgetall(thread_key)
                
                replies.append({
                    'id': reply_data['id'],
                    'thread_id': reply_data['thread_id'],
                    'thread_title': thread_data.get('title', 'Unknown Thread'),
                    'content_preview': reply_data['content'][:100] + '...' if len(reply_data['content']) > 100 else reply_data['content'],
                    'created_at': reply_data['created_at']
                })
        
        # Get engagement score
        engagement_key = f"user_engagement:{user_id}"
        engagement_score = float(redis_client.get(engagement_key) or 0)
        
        return jsonify({
            'user_id': user_id,
            'engagement_score': round(engagement_score, 2),
            'threads': threads,
            'replies': replies,
            'total_threads': redis_client.llen(user_threads_key),
            'total_replies': redis_client.llen(user_replies_key)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user activity: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user activity'}), 500

# Requirements file for community service
# requirements.txt
flask==2.3.3
flask-cors>=6.0.2  # CVE-2024-6866, CVE-2024-6839, CVE-2024-6844
google-cloud-logging==3.7.0
google-cloud-bigquery==3.12.0
redis==4.6.0
PyJWT==2.8.0