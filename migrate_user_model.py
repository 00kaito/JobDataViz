#!/usr/bin/env python3
"""
Database migration script to update User model:
- Remove username field
- Rename preferred_category to employment_category
- Set default employment_category for existing users
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Run the database migration"""
    try:
        # Import after setting path
        from models import db, User
        from app import server
        
        with server.app_context():
            print("Starting database migration...")
            
            # Check if we need to run migration by checking table structure
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            print(f"Current columns: {columns}")
            
            # Step 1: Add employment_category column if it doesn't exist
            if 'employment_category' not in columns:
                print("Adding employment_category column...")
                db.engine.execute("""
                    ALTER TABLE users ADD COLUMN employment_category VARCHAR(100) DEFAULT 'Frontend';
                """)
                
            # Step 2: Migrate data from preferred_category if it exists
            if 'preferred_category' in columns:
                print("Migrating data from preferred_category to employment_category...")
                # Map old categories to new ones
                category_mapping = {
                    'IT': 'FullStack',
                    'Finance': 'PM / ERP & Business',
                    'Marketing': 'PM / ERP & Business',
                    'Sales': 'PM / ERP & Business',
                    'HR': 'PM / ERP & Business',
                    'Operations': 'Admin / Devops & Infra',
                    'Engineering': 'Backend',
                    'Healthcare': 'PM / ERP & Business',
                    'Education': 'PM / ERP & Business',
                    'Other': 'FullStack'
                }
                
                # Update employment_category based on preferred_category
                users = User.query.all()
                for user in users:
                    if hasattr(user, 'preferred_category') and user.preferred_category:
                        new_category = category_mapping.get(user.preferred_category, 'FullStack')
                        db.engine.execute(f"""
                            UPDATE users SET employment_category = '{new_category}' 
                            WHERE id = {user.id};
                        """)
                
                # Drop the old preferred_category column
                print("Dropping preferred_category column...")
                try:
                    db.engine.execute("ALTER TABLE users DROP COLUMN preferred_category;")
                except Exception as e:
                    print(f"Warning: Could not drop preferred_category column: {e}")
            
            # Step 3: Remove username column if it exists
            if 'username' in columns:
                print("Dropping username column...")
                try:
                    db.engine.execute("ALTER TABLE users DROP COLUMN username;")
                except Exception as e:
                    print(f"Warning: Could not drop username column: {e}")
            
            # Step 4: Make sure employment_category is not nullable
            print("Setting employment_category as NOT NULL...")
            try:
                db.engine.execute("""
                    ALTER TABLE users ALTER COLUMN employment_category SET NOT NULL;
                """)
            except Exception as e:
                print(f"Warning: Could not set employment_category as NOT NULL: {e}")
            
            # Step 5: Make sure first_name is not nullable
            print("Setting first_name as NOT NULL...")
            try:
                db.engine.execute("""
                    ALTER TABLE users ALTER COLUMN first_name SET NOT NULL;
                """)
            except Exception as e:
                print(f"Warning: Could not set first_name as NOT NULL: {e}")
            
            print("Migration completed successfully!")
            
            # Verify the changes
            inspector = db.inspect(db.engine)
            new_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"New columns: {new_columns}")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    if migrate_database():
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)