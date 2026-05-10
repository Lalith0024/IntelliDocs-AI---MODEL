"""Google OAuth token verification and handling"""
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings

class GoogleTokenError(Exception):
    """Raised when Google token verification fails"""
    pass

def verify_google_token(id_token_str: str) -> dict:
    """
    Verify Google ID token and extract user information.
    
    Args:
        id_token_str: The ID token from Google OAuth
        
    Returns:
        dict: User info containing email, name, picture, google_id
        
    Raises:
        GoogleTokenError: If token verification fails
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Verify token is from expected issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise GoogleTokenError("Invalid token issuer")
        
        # Extract user info
        user_info = {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
        
        return user_info
        
    except Exception as e:
        raise GoogleTokenError(f"Token verification failed: {str(e)}")
