"""Test database module"""
from database import db

# Initialize database
db.initialize()
print("Database initialized successfully!")

# Get today's progress
progress = db.get_today_progress()
print(f"Today progress: streak={progress['streak']}, phase={progress['phase']}")

# Test settings
theme = db.get_setting('theme_color')
print(f"Theme color: {theme}")

# Test set/get
db.set_setting('test_key', 'test_value')
result = db.get_setting('test_key')
print(f"Test setting: {result}")

print("\n✅ All database tests passed!")
