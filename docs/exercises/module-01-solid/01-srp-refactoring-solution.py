#!/usr/bin/env python3
"""
Solution for SRP Refactoring Exercise
Module 01: SOLID Principles - Single Responsibility Principle

This solution demonstrates proper application of SRP by separating
the UserService class into specialized classes, each with a single responsibility.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sqlite3


# =============================================================================
# DATA MODELS
# =============================================================================


class User:
    """Domain model for User entity"""

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ):
        self.id: Optional[int] = None
        self.username = username
        self.email = email
        self.password = password  # В реальной системе должен быть хешированный
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.now()
        self.is_active = True

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"


# =============================================================================
# VALIDATION LAYER (Single Responsibility: Data Validation)
# =============================================================================


class UserValidator:
    """
    Responsible ONLY for user data validation.

    💡 Простыми словами: Этот класс проверяет, правильно ли заполнены данные пользователя.
    Он НЕ сохраняет данные, НЕ отправляет email - только проверяет.

    Single Responsibility Principle (SRP):
    - ✅ Одна ответственность: валидация данных
    - ❌ НЕ сохраняет в БД
    - ❌ НЕ отправляет email
    - ❌ НЕ обрабатывает бизнес-логику

    Example:
        >>> validator = UserValidator()
        >>> user_data = {
        ...     'username': 'john_doe',
        ...     'email': 'john@example.com',
        ...     'password': 'securepass123'
        ... }
        >>> is_valid = validator.validate_user_data(user_data)
        >>> print(is_valid)
        True
    """

    def validate_user_data(self, user_data: Dict[str, Any]) -> bool:
        """
        Validates user data according to business rules

        Args:
            user_data: Dictionary containing user information

        Returns:
            bool: True if data is valid, False otherwise

        Raises:
            ValueError: If data is invalid with specific error message
        """
        username = user_data.get("username")
        if (
            not username
            or not isinstance(username, str)
            or not self._validate_username(username)
        ):
            raise ValueError(
                "Username must be 3-50 characters and contain only letters, numbers, and underscores"
            )

        email = user_data.get("email")
        if not email or not isinstance(email, str) or not self._validate_email(email):
            raise ValueError("Invalid email format")

        password = user_data.get("password")
        if (
            not password
            or not isinstance(password, str)
            or not self._validate_password(password)
        ):
            raise ValueError("Password must be at least 8 characters long")

        return True

    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        if not username or not isinstance(username, str):
            return False
        if len(username) < 3 or len(username) > 50:
            return False
        return username.replace(
            "_", ""
        ).isalnum()  # Allow letters, numbers, underscores

    def _validate_email(self, email: str) -> bool:
        """Validate email format (basic validation)"""
        if not email or not isinstance(email, str):
            return False
        return "@" in email and "." in email.split("@")[1]

    def _validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False
        return len(password) >= 8


# =============================================================================
# PERSISTENCE LAYER (Single Responsibility: Database Operations)
# =============================================================================


class UserRepository:
    """Responsible ONLY for user data persistence"""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP,
                    is_active BOOLEAN
                )
            """)

    def save_user(self, user: User) -> User:
        """
        Save user to database

        Args:
            user: User object to save

        Returns:
            User: User object with assigned ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (username, email, password, first_name, last_name, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user.username,
                    user.email,
                    user.password,
                    user.first_name,
                    user.last_name,
                    user.created_at,
                    user.is_active,
                ),
            )

            user.id = cursor.lastrowid
            return user

    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if row:
                return self._row_to_user(row)
            return None

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

            if row:
                return self._row_to_user(row)
            return None

    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert database row to User object"""
        user = User(
            row["username"],
            row["email"],
            row["password"],
            row["first_name"],
            row["last_name"],
        )
        user.id = row["id"]
        user.created_at = datetime.fromisoformat(row["created_at"])
        user.is_active = bool(row["is_active"])
        return user


# =============================================================================
# NOTIFICATION LAYER (Single Responsibility: Email Communication)
# =============================================================================


class EmailService:
    """Responsible ONLY for sending emails"""

    def __init__(self, smtp_host: str = "localhost", smtp_port: int = 587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_welcome_email(self, user: User) -> bool:
        """
        Send welcome email to new user

        Args:
            user: User to send email to

        Returns:
            bool: True if email sent successfully
        """
        subject = "Welcome to Our Platform!"
        body = self._create_welcome_email_body(user)

        return self._send_email(user.email, subject, body)

    def send_confirmation_email(self, user: User, confirmation_link: str) -> bool:
        """Send email confirmation link"""
        subject = "Please Confirm Your Email"
        body = f"""
        Hello {user.full_name()},
        
        Please click the link below to confirm your email address:
        {confirmation_link}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Team
        """

        return self._send_email(user.email, subject, body)

    def _create_welcome_email_body(self, user: User) -> str:
        """Create welcome email content"""
        return f"""
        Hello {user.full_name()},
        
        Welcome to our platform! Your account '{user.username}' has been successfully created.
        
        You can now:
        - Access all platform features
        - Connect with other users
        - Customize your profile
        
        If you have any questions, don't hesitate to contact our support team.
        
        Best regards,
        The Team
        """

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via SMTP

        Note: In this example, we're just simulating email sending
        In production, you would implement actual SMTP sending
        """
        try:
            # Simulate email sending
            print(f"📧 SENDING EMAIL TO: {to_email}")
            print(f"📧 SUBJECT: {subject}")
            print(f"📧 BODY: {body}")
            print("✅ Email sent successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


# =============================================================================
# REPORTING LAYER (Single Responsibility: Report Generation)
# =============================================================================


class ReportGenerator:
    """Responsible ONLY for generating reports"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def generate_user_registration_report(self) -> str:
        """Generate user registration statistics report"""
        # In a real implementation, you would query the database for statistics
        report = f"""
        📊 USER REGISTRATION REPORT
        ===========================
        
        📈 Registration Statistics:
        - Total Users: [would query database]
        - Active Users: [would query database]  
        - Today's Registrations: [would query database]
        - This Week's Registrations: [would query database]
        
        📍 Top Registration Sources:
        - Direct: 45%
        - Referral: 30%
        - Social Media: 25%
        
        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

        return report

    def generate_user_activity_report(self, user_id: int) -> str:
        """Generate individual user activity report"""
        return f"""
        👤 USER ACTIVITY REPORT
        =======================
        User ID: {user_id}
        
        📊 Activity Summary:
        - Last Login: [would query from activity table]
        - Total Sessions: [would calculate from logs]
        - Features Used: [would analyze usage patterns]
        
        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """


# =============================================================================
# BUSINESS LOGIC LAYER (Single Responsibility: User Business Logic)
# =============================================================================


class UserService:
    """
    Responsible ONLY for user-related business logic and orchestration

    This class now follows SRP by:
    - Only containing business logic
    - Delegating validation to UserValidator
    - Delegating persistence to UserRepository
    - Delegating email sending to EmailService
    - Delegating reporting to ReportGenerator
    """

    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        email_service: EmailService,
        report_generator: ReportGenerator,
    ):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.report_generator = report_generator

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create new user with proper validation, persistence, and notifications

        Args:
            user_data: Dictionary containing user information

        Returns:
            User: Created user object

        Raises:
            ValueError: If validation fails
            RuntimeError: If user creation fails
        """
        try:
            # 1. Validate data (delegate to validator)
            self.validator.validate_user_data(user_data)

            # 2. Check for existing users (business logic)
            if self._user_exists(user_data["username"], user_data["email"]):
                raise ValueError("User with this username or email already exists")

            # 3. Create user object (business logic)
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],  # Should be hashed in production
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
            )

            # 4. Save to database (delegate to repository)
            user = self.repository.save_user(user)

            # 5. Send welcome email (delegate to email service)
            self.email_service.send_welcome_email(user)

            # 6. Log successful creation (business logic)
            print(f"✅ User '{user.username}' created successfully with ID {user.id}")

            return user

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle unexpected errors
            raise RuntimeError(f"Failed to create user: {str(e)}")

    def _user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists (business logic)"""
        existing_by_username = self.repository.find_by_username(username)
        existing_by_email = self.repository.find_by_email(email)

        return existing_by_username is not None or existing_by_email is not None

    def get_user_profile(self, username: str) -> Optional[User]:
        """Get user profile information"""
        return self.repository.find_by_username(username)

    def generate_user_report(self, report_type: str = "registration") -> str:
        """Generate user reports (business logic coordination)"""
        if report_type == "registration":
            return self.report_generator.generate_user_registration_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")


# =============================================================================
# DEPENDENCY INJECTION SETUP
# =============================================================================


def create_user_service() -> UserService:
    """
    Factory function to create UserService with all dependencies
    This demonstrates proper dependency injection
    """
    # Create dependencies
    validator = UserValidator()
    repository = UserRepository()  # Using in-memory database for demo
    email_service = EmailService()
    report_generator = ReportGenerator(repository)

    # Inject dependencies into service
    return UserService(validator, repository, email_service, report_generator)


# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================


def main():
    """Demonstrate the refactored UserService following SRP"""
    print("🎯 SRP Refactoring Demo")
    print("=" * 50)

    # Create service with dependency injection
    user_service = create_user_service()

    # Test data
    test_users = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "password": "anothersecurepass456",
            "first_name": "Jane",
            "last_name": "Smith",
        },
    ]

    # Test user creation
    for user_data in test_users:
        try:
            print(f"\n👤 Creating user: {user_data['username']}")
            user = user_service.create_user(user_data)
            print(f"✅ Success: {user}")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Test duplicate user creation (should fail)
    print("\n🔄 Testing duplicate user creation...")
    try:
        duplicate_user = test_users[0].copy()
        user_service.create_user(duplicate_user)
    except Exception as e:
        print(f"✅ Expected error for duplicate: {e}")

    # Test invalid data (should fail)
    print("\n🔄 Testing invalid user data...")
    try:
        invalid_user = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "123",  # Too short
        }
        user_service.create_user(invalid_user)
    except Exception as e:
        print(f"✅ Expected validation error: {e}")

    # Test report generation
    print("\n📊 Generating user registration report...")
    report = user_service.generate_user_report("registration")
    print(report)

    # Demonstrate profile retrieval
    print("\n👤 Retrieving user profile...")
    profile = user_service.get_user_profile("john_doe")
    if profile:
        print(f"Found user: {profile.full_name()} ({profile.email})")

    print("\n" + "=" * 50)
    print("🎯 SRP Refactoring Demo Complete!")
    print("\nKey SRP Benefits Demonstrated:")
    print("✅ UserValidator - Single responsibility: Data validation")
    print("✅ UserRepository - Single responsibility: Data persistence")
    print("✅ EmailService - Single responsibility: Email notifications")
    print("✅ ReportGenerator - Single responsibility: Report generation")
    print("✅ UserService - Single responsibility: Business logic orchestration")
    print("\nEach class now has only ONE reason to change! 🎉")


if __name__ == "__main__":
    main()
