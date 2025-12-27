"""
User Management System - Roles, permissions, and access control

Provides:
- User authentication and authorization
- Role-based access control (RBAC)
- Permission management
- User activity tracking
- Team collaboration features
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
from src.infrastructure import FirestoreManager
from src.monitoring import StructuredLogger


class Role(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    EDITOR = "editor"
    CONTENT_CREATOR = "content_creator"
    VIEWER = "viewer"
    API_USER = "api_user"


class Permission(Enum):
    """Granular permissions"""
    # Project permissions
    CREATE_PROJECT = "create_project"
    READ_PROJECT = "read_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    
    # Content permissions
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    APPROVE_CONTENT = "approve_content"
    PUBLISH_CONTENT = "publish_content"
    DELETE_CONTENT = "delete_content"
    
    # Agent permissions
    USE_RESEARCH_AGENT = "use_research_agent"
    USE_CONTENT_AGENT = "use_content_agent"
    USE_EDITOR_AGENT = "use_editor_agent"
    USE_SEO_AGENT = "use_seo_agent"
    USE_IMAGE_AGENT = "use_image_agent"
    USE_VIDEO_AGENT = "use_video_agent"
    USE_AUDIO_AGENT = "use_audio_agent"
    USE_PUBLISHER_AGENT = "use_publisher_agent"
    
    # System permissions
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_COSTS = "view_costs"
    MANAGE_BUDGET = "manage_budget"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    Role.EDITOR: [
        Permission.CREATE_PROJECT,
        Permission.READ_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.APPROVE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.USE_RESEARCH_AGENT,
        Permission.USE_CONTENT_AGENT,
        Permission.USE_EDITOR_AGENT,
        Permission.USE_SEO_AGENT,
        Permission.USE_IMAGE_AGENT,
        Permission.USE_VIDEO_AGENT,
        Permission.USE_AUDIO_AGENT,
        Permission.USE_PUBLISHER_AGENT,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_COSTS
    ],
    Role.CONTENT_CREATOR: [
        Permission.CREATE_PROJECT,
        Permission.READ_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.USE_RESEARCH_AGENT,
        Permission.USE_CONTENT_AGENT,
        Permission.USE_EDITOR_AGENT,
        Permission.USE_SEO_AGENT,
        Permission.USE_IMAGE_AGENT,
        Permission.USE_VIDEO_AGENT,
        Permission.USE_AUDIO_AGENT,
        Permission.VIEW_ANALYTICS
    ],
    Role.VIEWER: [
        Permission.READ_PROJECT,
        Permission.VIEW_ANALYTICS
    ],
    Role.API_USER: [
        Permission.CREATE_PROJECT,
        Permission.READ_PROJECT,
        Permission.CREATE_CONTENT,
        Permission.USE_RESEARCH_AGENT,
        Permission.USE_CONTENT_AGENT
    ]
}


class UserManager:
    """User management and authentication"""
    
    def __init__(self):
        """Initialize user manager"""
        self.logger = StructuredLogger(name='user_manager')
        self.db = FirestoreManager()
        self.users_collection = 'users'
        self.sessions_collection = 'user_sessions'
        self.teams_collection = 'teams'
    
    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        role: Role = Role.CONTENT_CREATOR,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            email: User email
            password: User password
            name: User full name
            role: User role
            metadata: Optional additional metadata
            
        Returns:
            Created user data
        """
        try:
            # Check if user already exists
            existing = self._get_user_by_email(email)
            if existing:
                raise ValueError(f"User with email {email} already exists")
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Create user document
            user_id = f"user_{secrets.token_hex(8)}"
            user_data = {
                'user_id': user_id,
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'role': role.value,
                'permissions': [p.value for p in ROLE_PERMISSIONS[role]],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_login': None,
                'is_active': True,
                'metadata': metadata or {}
            }
            
            # Save to Firestore (simulated)
            # self.db.collection(self.users_collection).document(user_id).set(user_data)
            
            self.logger.info(f"User created: {email}", user_id=user_id, role=role.value)
            
            # Return user data without password hash
            user_data.pop('password_hash')
            return user_data
            
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}", email=email)
            raise
    
    def authenticate(
        self,
        email: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data with session token if successful, None otherwise
        """
        try:
            user = self._get_user_by_email(email)
            
            if not user:
                self.logger.warning(f"Authentication failed: User not found", email=email)
                return None
            
            if not user.get('is_active'):
                self.logger.warning(f"Authentication failed: User inactive", email=email)
                return None
            
            # Verify password
            password_hash = self._hash_password(password)
            if password_hash != user.get('password_hash'):
                self.logger.warning(f"Authentication failed: Invalid password", email=email)
                return None
            
            # Create session
            session_token = self._create_session(user['user_id'])
            
            # Update last login
            user['last_login'] = datetime.utcnow().isoformat()
            # self.db.collection(self.users_collection).document(user['user_id']).update({
            #     'last_login': user['last_login']
            # })
            
            self.logger.info(f"User authenticated: {email}", user_id=user['user_id'])
            
            # Return user data without password hash
            user.pop('password_hash')
            user['session_token'] = session_token
            
            return user
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}", email=email)
            return None
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User data if session is valid, None otherwise
        """
        try:
            # Get session (simulated)
            session = self._get_session(session_token)
            
            if not session:
                return None
            
            # Check if session expired
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < datetime.utcnow():
                self.logger.warning("Session expired", session_token=session_token)
                return None
            
            # Get user
            user = self._get_user_by_id(session['user_id'])
            if not user or not user.get('is_active'):
                return None
            
            # Return user data without password hash
            user.pop('password_hash', None)
            return user
            
        except Exception as e:
            self.logger.error(f"Session validation error: {e}")
            return None
    
    def has_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user_id: User ID
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        try:
            user = self._get_user_by_id(user_id)
            if not user:
                return False
            
            return permission.value in user.get('permissions', [])
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}", user_id=user_id)
            return False
    
    def update_user_role(
        self,
        user_id: str,
        new_role: Role,
        admin_user_id: str
    ) -> bool:
        """
        Update user's role
        
        Args:
            user_id: User ID to update
            new_role: New role
            admin_user_id: Admin performing the action
            
        Returns:
            Success status
        """
        try:
            # Check admin permission
            if not self.has_permission(admin_user_id, Permission.MANAGE_USERS):
                self.logger.warning(
                    "Unauthorized role update attempt",
                    admin_user_id=admin_user_id,
                    target_user_id=user_id
                )
                return False
            
            # Update role and permissions
            new_permissions = [p.value for p in ROLE_PERMISSIONS[new_role]]
            
            # self.db.collection(self.users_collection).document(user_id).update({
            #     'role': new_role.value,
            #     'permissions': new_permissions,
            #     'updated_at': datetime.utcnow().isoformat()
            # })
            
            self.logger.info(
                f"User role updated",
                user_id=user_id,
                new_role=new_role.value,
                admin_user_id=admin_user_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update user role: {e}", user_id=user_id)
            return False
    
    def deactivate_user(
        self,
        user_id: str,
        admin_user_id: str
    ) -> bool:
        """Deactivate a user account"""
        try:
            if not self.has_permission(admin_user_id, Permission.MANAGE_USERS):
                return False
            
            # self.db.collection(self.users_collection).document(user_id).update({
            #     'is_active': False,
            #     'updated_at': datetime.utcnow().isoformat()
            # })
            
            self.logger.info(f"User deactivated", user_id=user_id, admin_user_id=admin_user_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate user: {e}", user_id=user_id)
            return False
    
    def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user activity summary
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Activity summary
        """
        try:
            # Simulated activity data
            return {
                'user_id': user_id,
                'time_range_days': days,
                'projects_created': 12,
                'content_generated': 45,
                'agents_used': {
                    'research': 12,
                    'content': 45,
                    'editor': 38,
                    'seo': 42,
                    'image': 15
                },
                'total_cost': 28.50,
                'login_count': 23,
                'last_activity': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity: {e}", user_id=user_id)
            return {}
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        # In production, use bcrypt or Argon2
        # import bcrypt
        # return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        # Simulated - in production, query Firestore
        # users = self.db.collection(self.users_collection).where('email', '==', email).get()
        # return users[0].to_dict() if users else None
        
        # Simulated user for testing
        if email == "admin@example.com":
            return {
                'user_id': 'user_admin123',
                'email': email,
                'password_hash': self._hash_password('admin123'),
                'name': 'Admin User',
                'role': Role.ADMIN.value,
                'permissions': [p.value for p in ROLE_PERMISSIONS[Role.ADMIN]],
                'is_active': True
            }
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        # Simulated - in production, query Firestore
        # doc = self.db.collection(self.users_collection).document(user_id).get()
        # return doc.to_dict() if doc.exists else None
        
        if user_id == 'user_admin123':
            return {
                'user_id': user_id,
                'email': 'admin@example.com',
                'password_hash': self._hash_password('admin123'),
                'name': 'Admin User',
                'role': Role.ADMIN.value,
                'permissions': [p.value for p in ROLE_PERMISSIONS[Role.ADMIN]],
                'is_active': True
            }
        return None
    
    def _create_session(self, user_id: str) -> str:
        """Create a new session token"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        session_data = {
            'session_token': session_token,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        
        # Save to Firestore (simulated)
        # self.db.collection(self.sessions_collection).document(session_token).set(session_data)
        
        return session_token
    
    def _get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        # Simulated - in production, query Firestore
        # doc = self.db.collection(self.sessions_collection).document(session_token).get()
        # return doc.to_dict() if doc.exists else None
        
        # Simulated session
        return {
            'session_token': session_token,
            'user_id': 'user_admin123',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }


class TeamManager:
    """Team collaboration management"""
    
    def __init__(self):
        """Initialize team manager"""
        self.logger = StructuredLogger(name='team_manager')
        self.db = FirestoreManager()
        self.teams_collection = 'teams'
    
    def create_team(
        self,
        name: str,
        owner_id: str,
        members: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new team"""
        try:
            team_id = f"team_{secrets.token_hex(8)}"
            team_data = {
                'team_id': team_id,
                'name': name,
                'owner_id': owner_id,
                'members': members or [],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            # Save to Firestore (simulated)
            # self.db.collection(self.teams_collection).document(team_id).set(team_data)
            
            self.logger.info(f"Team created: {name}", team_id=team_id, owner_id=owner_id)
            return team_data
            
        except Exception as e:
            self.logger.error(f"Failed to create team: {e}", name=name)
            raise
    
    def add_member(
        self,
        team_id: str,
        user_id: str,
        role: str = 'member'
    ) -> bool:
        """Add a member to a team"""
        try:
            # Update team members (simulated)
            # self.db.collection(self.teams_collection).document(team_id).update({
            #     'members': firestore.ArrayUnion([{
            #         'user_id': user_id,
            #         'role': role,
            #         'joined_at': datetime.utcnow().isoformat()
            #     }])
            # })
            
            self.logger.info(f"Member added to team", team_id=team_id, user_id=user_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add team member: {e}", team_id=team_id)
            return False
    
    def get_team_projects(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a team"""
        # Simulated - in production, query projects by team_id
        return []
