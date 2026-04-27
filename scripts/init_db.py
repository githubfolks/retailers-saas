import sys
import os

# Add the app directory to the path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app.models
from app.core.database import Base, engine

def init_db():
    print("Initializing database...")
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables:")
        print("- tenants")
        print("- orders")
        print("- products")
        print("- customers")
        print("- conversation_states")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
