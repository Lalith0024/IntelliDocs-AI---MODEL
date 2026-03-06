import os
import sys
from pathlib import Path

# Add project root to path so 'app' can be imported
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.main import app

# For Vercel, the 'app' variable must be available
