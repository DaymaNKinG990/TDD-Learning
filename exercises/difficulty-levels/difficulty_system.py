#!/usr/bin/env python3
"""
Difficulty Levels System for Programming Tasks
Module: All Modules - Adaptive Learning System

This system provides three difficulty levels for each programming task:
- Beginner: Basic implementation with guided steps
- Intermediate: Standard implementation with moderate complexity
- Advanced: Complex implementation with additional features

Features:
- Adaptive task generation
- Progressive skill building
- Personalized learning paths
- Performance tracking
- Automatic level recommendation
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# =============================================================================
# DIFFICULTY SYSTEM CORE
# =============================================================================


class DifficultyLevel(Enum):
    """Difficulty level enumeration"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SkillDomain(Enum):
    """Skill domain enumeration"""

    SOLID_PRINCIPLES = "solid_principles"
    DESIGN_PATTERNS = "design_patterns"
    ARCHITECTURE = "architecture"
    DOMAIN_DRIVEN_DESIGN = "domain_driven_design"
    PROJECT_MANAGEMENT = "project_management"


@dataclass
class SkillRequirement:
    """Skill requirement for a task"""

    domain: SkillDomain
    level: int  # 1-10 scale
    description: str


@dataclass
class LearningObjective:
    """Learning objective for a task"""

    description: str
    skill_requirements: list[SkillRequirement]
    assessment_criteria: list[str]


@dataclass
class TaskTemplate:
    """Template for generating tasks at different difficulty levels"""

    id: str
    title: str
    description: str
    module: str
    base_objectives: list[LearningObjective]
    estimated_time_minutes: dict[DifficultyLevel, int]
    prerequisites: list[str] = field(default_factory=list)

    def generate_task(self, level: DifficultyLevel) -> "ProgrammingTask":
        """Generate task for specific difficulty level"""
        generator = TaskGenerator()
        return generator.generate_task(self, level)


@dataclass
class ProgrammingTask:
    """Complete programming task with all materials"""

    template_id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    objectives: list[LearningObjective]
    starter_code: str
    instructions: list[str]
    hints: list[str]
    test_cases: list[str]
    solution_template: str
    grading_rubric: dict[str, int]
    estimated_time: int
    resources: list[str] = field(default_factory=list)


@dataclass
class StudentProgress:
    """Track student progress across difficulty levels"""

    student_id: str
    skill_levels: dict[SkillDomain, int] = field(default_factory=dict)
    completed_tasks: list[str] = field(default_factory=list)
    current_level_recommendations: dict[str, DifficultyLevel] = field(
        default_factory=dict
    )
    performance_history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        # Initialize skill levels
        for domain in SkillDomain:
            if domain not in self.skill_levels:
                self.skill_levels[domain] = 1


# =============================================================================
# TASK GENERATORS FOR EACH DIFFICULTY LEVEL
# =============================================================================


class TaskGenerator:
    """
    Generate tasks based on difficulty level.

    💡 Простыми словами: Это "фабрика заданий" - она создает задания разной сложности
    из одного шаблона. Как повар готовит блюдо разной остроты из одного рецепта.

    Example:
        >>> generator = TaskGenerator()
        >>> template = TaskTemplate(...)
        >>> beginner_task = generator.generate_task(template, DifficultyLevel.BEGINNER)
        >>> print(beginner_task.title)
        '🟢 SRP Refactoring (Beginner)'
    """

    def generate_task(
        self, template: TaskTemplate, level: DifficultyLevel
    ) -> ProgrammingTask:
        """
        Generate task for specific difficulty level.

        💡 Простыми словами: Берет шаблон задания и создает версию нужной сложности.
        Для начинающих - больше подсказок, для продвинутых - меньше.

        Args:
            template: Шаблон задания (что нужно сделать)
            level: Уровень сложности (beginner/intermediate/advanced)

        Returns:
            ProgrammingTask: Полное задание с инструкциями, кодом, тестами

        Example:
            >>> task = generator.generate_task(template, DifficultyLevel.BEGINNER)
            >>> print(f"Time: {task.estimated_time} min")
            >>> print(f"Hints: {len(task.hints)}")
        """
        if level == DifficultyLevel.BEGINNER:
            return self._generate_beginner_task(template)
        elif level == DifficultyLevel.INTERMEDIATE:
            return self._generate_intermediate_task(template)
        else:
            return self._generate_advanced_task(template)

    def _generate_beginner_task(self, template: TaskTemplate) -> ProgrammingTask:
        """
        Generate beginner-level task with extensive guidance.

        💡 Простыми словами: Создает задание для начинающих - много подсказок,
        готовый каркас кода, пошаговые инструкции. Как обучение вождению с инструктором.

        Features:
        - Detailed step-by-step instructions
        - Extensive code scaffolding (много готового кода)
        - Multiple hints at each step
        - Simple test cases
        - Extended time estimate

        Args:
            template: Шаблон задания

        Returns:
            ProgrammingTask: Задание для начинающих
        """
        return ProgrammingTask(
            template_id=template.id,
            title=f"🟢 {template.title} (Beginner)",
            description=f"{template.description}\n\n🎯 **Beginner Level**: This task includes detailed step-by-step instructions, extensive code scaffolding, and guided implementation.",
            difficulty=DifficultyLevel.BEGINNER,
            objectives=self._simplify_objectives(template.base_objectives),
            starter_code=self._generate_beginner_starter_code(template),
            instructions=self._generate_beginner_instructions(template),
            hints=self._generate_beginner_hints(template),
            test_cases=self._generate_beginner_tests(template),
            solution_template=self._generate_beginner_solution_template(template),
            grading_rubric=self._generate_beginner_rubric(template),
            estimated_time=template.estimated_time_minutes[DifficultyLevel.BEGINNER],
            resources=self._generate_beginner_resources(template),
        )

    def _generate_intermediate_task(self, template: TaskTemplate) -> ProgrammingTask:
        """Generate intermediate-level task"""
        return ProgrammingTask(
            template_id=template.id,
            title=f"🟡 {template.title} (Intermediate)",
            description=f"{template.description}\n\n🎯 **Intermediate Level**: This task provides moderate guidance with some autonomy in implementation decisions.",
            difficulty=DifficultyLevel.INTERMEDIATE,
            objectives=template.base_objectives,
            starter_code=self._generate_intermediate_starter_code(template),
            instructions=self._generate_intermediate_instructions(template),
            hints=self._generate_intermediate_hints(template),
            test_cases=self._generate_intermediate_tests(template),
            solution_template=self._generate_intermediate_solution_template(template),
            grading_rubric=self._generate_intermediate_rubric(template),
            estimated_time=template.estimated_time_minutes[
                DifficultyLevel.INTERMEDIATE
            ],
            resources=self._generate_intermediate_resources(template),
        )

    def _generate_advanced_task(self, template: TaskTemplate) -> ProgrammingTask:
        """Generate advanced-level task"""
        return ProgrammingTask(
            template_id=template.id,
            title=f"🔴 {template.title} (Advanced)",
            description=f"{template.description}\n\n🎯 **Advanced Level**: This task requires independent problem-solving, architectural decisions, and additional feature implementation.",
            difficulty=DifficultyLevel.ADVANCED,
            objectives=self._enhance_objectives(template.base_objectives),
            starter_code=self._generate_advanced_starter_code(template),
            instructions=self._generate_advanced_instructions(template),
            hints=self._generate_advanced_hints(template),
            test_cases=self._generate_advanced_tests(template),
            solution_template=self._generate_advanced_solution_template(template),
            grading_rubric=self._generate_advanced_rubric(template),
            estimated_time=template.estimated_time_minutes[DifficultyLevel.ADVANCED],
            resources=self._generate_advanced_resources(template),
        )

    # Helper methods for code generation
    def _generate_beginner_starter_code(self, template: TaskTemplate) -> str:
        """Generate extensive starter code for beginners"""
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Beginner Level: SRP Refactoring Exercise
Follow the step-by-step instructions to refactor the UserService class.
"""

# Step 1: Create UserValidator class
class UserValidator:
    """TODO: Add class documentation"""

    def validate_user_data(self, user_data):
        """
        TODO: Implement user data validation

        Args:
            user_data (dict): User data to validate

        Returns:
            bool: True if valid, False otherwise

        Steps:
        1. Check if username is at least 3 characters
        2. Check if email contains @ symbol
        3. Check if password is at least 8 characters
        """
        # TODO: Implement validation logic
        pass


# Step 2: Create UserRepository class
class UserRepository:
    """TODO: Add class documentation"""

    def __init__(self):
        """Initialize the repository"""
        # TODO: Set up database connection or in-memory storage
        pass

    def save_user(self, user):
        """
        TODO: Implement user saving

        Args:
            user: User object to save

        Returns:
            User: Saved user object
        """
        # TODO: Implement save logic
        pass

    def find_by_username(self, username):
        """
        TODO: Implement user finding by username

        Args:
            username (str): Username to search for

        Returns:
            User or None: Found user or None
        """
        # TODO: Implement find logic
        pass


# Step 3: Create EmailService class
class EmailService:
    """TODO: Add class documentation"""

    def send_welcome_email(self, user):
        """
        TODO: Implement welcome email sending

        Args:
            user: User object to send email to

        Returns:
            bool: True if sent successfully
        """
        # TODO: Implement email sending logic
        pass


# Step 4: Create User domain model
class User:
    """TODO: Add class documentation"""

    def __init__(self, username, email, password):
        """TODO: Initialize user object"""
        # TODO: Set user properties
        pass


# Step 5: Refactor UserService to use dependencies
class UserService:
    """
    Refactored UserService following Single Responsibility Principle

    This class now only handles business logic orchestration.
    """

    def __init__(self, validator, repository, email_service):
        """
        TODO: Initialize dependencies

        Args:
            validator: UserValidator instance
            repository: UserRepository instance
            email_service: EmailService instance
        """
        # TODO: Store dependencies
        pass

    def create_user(self, user_data):
        """
        TODO: Implement user creation using injected dependencies

        Args:
            user_data (dict): User data

        Returns:
            User: Created user object

        Steps:
        1. Validate data using validator
        2. Create User object
        3. Save using repository
        4. Send welcome email using email service
        5. Return created user
        """
        # TODO: Implement using dependencies
        pass


# Step 6: Demonstrate dependency injection
def main():
    """TODO: Demonstrate the refactored system"""
    # TODO: Create dependencies
    # TODO: Create UserService with dependencies
    # TODO: Test user creation
    pass


if __name__ == "__main__":
    main()
'''

        return "# TODO: Implement starter code for " + template.id

    def _generate_beginner_instructions(self, template: TaskTemplate) -> list[str]:
        """Generate detailed step-by-step instructions for beginners"""
        if template.id == "srp_refactoring":
            return [
                "📋 **Step 1**: Complete the UserValidator class",
                "  • Implement the validate_user_data method",
                "  • Add proper validation for username, email, and password",
                "  • Return True if all validations pass, False otherwise",
                "",
                "📋 **Step 2**: Complete the UserRepository class",
                "  • Implement the __init__ method to set up storage",
                "  • Implement save_user to store user data",
                "  • Implement find_by_username to retrieve users",
                "",
                "📋 **Step 3**: Complete the EmailService class",
                "  • Implement send_welcome_email method",
                "  • For now, just print a message (simulate email sending)",
                "  • Return True to indicate success",
                "",
                "📋 **Step 4**: Complete the User class",
                "  • Add __init__ method with username, email, password parameters",
                "  • Store the parameters as instance variables",
                "  • Add a __str__ method for easy printing",
                "",
                "📋 **Step 5**: Complete the UserService class",
                "  • Store the injected dependencies in __init__",
                "  • Implement create_user method using the dependencies",
                "  • Follow the steps outlined in the method docstring",
                "",
                "📋 **Step 6**: Complete the main function",
                "  • Create instances of UserValidator, UserRepository, EmailService",
                "  • Create UserService with these dependencies",
                "  • Test creating a user with sample data",
                "",
                "🎯 **Success Criteria**:",
                "  • All classes have single responsibilities",
                "  • Dependencies are properly injected",
                "  • User creation works end-to-end",
                "  • Code follows SRP principles",
            ]

        return ["Complete the implementation following the TODO comments"]

    def _generate_beginner_hints(self, _template: TaskTemplate) -> list[str]:
        """Generate helpful hints for beginners"""
        return [
            "💡 Start with the simplest class first (usually the data models)",
            "💡 Implement one method at a time and test it",
            "💡 Use print statements to debug your implementation",
            "💡 Remember: each class should have only one reason to change",
            "💡 If you're stuck, review the SOLID principles documentation",
            "💡 Ask yourself: 'What is this class responsible for?'",
        ]

    def _generate_intermediate_instructions(self, template: TaskTemplate) -> list[str]:
        """Generate instructions for intermediate level"""
        return self._generate_beginner_instructions(template)

    def _generate_intermediate_hints(self, template: TaskTemplate) -> list[str]:
        """Generate hints for intermediate level"""
        return self._generate_beginner_hints(template)

    def _generate_advanced_instructions(self, template: TaskTemplate) -> list[str]:
        """Generate instructions for advanced level"""
        return self._generate_beginner_instructions(template)

    def _generate_advanced_hints(self, template: TaskTemplate) -> list[str]:
        """Generate hints for advanced level"""
        return self._generate_beginner_hints(template)

    def _generate_intermediate_starter_code(self, template: TaskTemplate) -> str:
        """Generate moderate starter code for intermediate level"""
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Intermediate Level: SRP Refactoring Exercise
Refactor the monolithic UserService into separate classes following SRP.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


# TODO: Implement UserValidator class
class UserValidator:
    """Handles user data validation"""
    pass


# TODO: Implement UserRepository interface and implementation
class IUserRepository(ABC):
    """Interface for user persistence"""
    pass


class UserRepository(IUserRepository):
    """Concrete implementation of user persistence"""
    pass


# TODO: Implement EmailService
class EmailService:
    """Handles email notifications"""
    pass


# TODO: Implement User domain model
class User:
    """User domain entity"""
    pass


# TODO: Refactor UserService to use dependency injection
class UserService:
    """
    Orchestrates user creation process using injected dependencies.
    Should only contain business logic, delegating specific responsibilities.
    """

    def __init__(self, validator: UserValidator, repository: IUserRepository, email_service: EmailService):
        # TODO: Store dependencies
        pass

    def create_user(self, user_data: Dict[str, Any]) -> User:
        # TODO: Implement user creation workflow
        pass


# TODO: Implement factory function for dependency injection
def create_user_service() -> UserService:
    """Factory function to create UserService with all dependencies"""
    pass


# TODO: Demonstrate the refactored system
def main():
    """Test the refactored UserService"""
    pass


if __name__ == "__main__":
    main()
'''

        return "# TODO: Implement starter code for " + template.id

    def _generate_advanced_starter_code(self, template: TaskTemplate) -> str:
        """Generate minimal starter code for advanced level"""
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Advanced Level: SRP Refactoring with Error Handling and Async Operations
Create a robust user management system with proper error handling,
logging, async operations, and additional enterprise features.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


# Domain Models
@dataclass
class User:
    """Enhanced User domain model with business methods"""
    # TODO: Implement comprehensive User entity
    pass


class UserRole(Enum):
    """User role enumeration"""
    # TODO: Define user roles
    pass


# Advanced Requirements:
# 1. Implement async repository operations
# 2. Add comprehensive error handling with custom exceptions
# 3. Add logging throughout the system
# 4. Implement validation with detailed error messages
# 5. Add user role management
# 6. Implement audit logging for user operations
# 7. Add configuration management
# 8. Implement retry mechanisms for external services
# 9. Add performance monitoring
# 10. Create comprehensive integration tests

# TODO: Design and implement the complete system architecture
# Consider: Error handling, async operations, logging, monitoring, testing

def main():
    """Advanced demonstration with error scenarios and monitoring"""
    # TODO: Implement advanced demonstration
    pass


if __name__ == "__main__":
    main()
'''

        return "# TODO: Implement minimal starter code for " + template.id

    def _simplify_objectives(
        self, objectives: list[LearningObjective]
    ) -> list[LearningObjective]:
        """Simplify learning objectives for beginners"""
        simplified = []
        for obj in objectives:
            # Reduce skill level requirements
            simplified_skills = []
            for skill in obj.skill_requirements:
                simplified_skills.append(
                    SkillRequirement(
                        skill.domain,
                        max(1, skill.level - 2),  # Reduce by 2 levels
                        f"Basic {skill.description}",
                    )
                )

            simplified.append(
                LearningObjective(
                    f"Basic {obj.description}",
                    simplified_skills,
                    obj.assessment_criteria[:3],  # Fewer criteria
                )
            )

        return simplified

    def _enhance_objectives(
        self, objectives: list[LearningObjective]
    ) -> list[LearningObjective]:
        """Enhance learning objectives for advanced level"""
        enhanced = []
        for obj in objectives:
            # Increase skill level requirements
            enhanced_skills = []
            for skill in obj.skill_requirements:
                enhanced_skills.append(
                    SkillRequirement(
                        skill.domain,
                        min(10, skill.level + 2),  # Increase by 2 levels
                        f"Advanced {skill.description}",
                    )
                )

            # Add additional requirements
            enhanced_skills.extend(
                [
                    SkillRequirement(SkillDomain.ARCHITECTURE, 7, "System Design"),
                    SkillRequirement(
                        SkillDomain.DESIGN_PATTERNS, 8, "Pattern Application"
                    ),
                ]
            )

            enhanced_criteria = obj.assessment_criteria + [
                "Error handling and edge cases",
                "Performance optimization",
                "Scalability considerations",
                "Security best practices",
                "Comprehensive testing",
            ]

            enhanced.append(
                LearningObjective(
                    f"Advanced {obj.description}", enhanced_skills, enhanced_criteria
                )
            )

        return enhanced

    def _generate_beginner_tests(self, _template: TaskTemplate) -> list[str]:
        """Generate basic tests for beginners"""
        return [
            "Test that all required classes exist",
            "Test that methods can be called without errors",
            "Test basic functionality with valid inputs",
            "Verify SRP compliance with simple checks",
        ]

    def _generate_intermediate_tests(self, _template: TaskTemplate) -> list[str]:
        """Generate moderate tests for intermediate level"""
        return [
            "Test all classes and their public interfaces",
            "Test error handling with invalid inputs",
            "Test dependency injection works correctly",
            "Verify design patterns are properly implemented",
            "Test edge cases and boundary conditions",
        ]

    def _generate_advanced_tests(self, _template: TaskTemplate) -> list[str]:
        """Generate comprehensive tests for advanced level"""
        return [
            "Unit tests for all components with 90%+ coverage",
            "Integration tests for complete workflows",
            "Performance tests under load",
            "Security tests for vulnerabilities",
            "Error recovery and resilience tests",
            "Concurrent access and thread safety tests",
            "Memory leak and resource management tests",
        ]

    def _generate_beginner_rubric(self, _template: TaskTemplate) -> dict[str, int]:
        """Generate grading rubric for beginners"""
        return {
            "Code Compiles and Runs": 20,
            "Basic Functionality": 25,
            "Follows Instructions": 20,
            "Code Organization": 15,
            "Comments and Documentation": 10,
            "SRP Basic Understanding": 10,
        }

    def _generate_intermediate_rubric(self, _template: TaskTemplate) -> dict[str, int]:
        """Generate grading rubric for intermediate level"""
        return {
            "Functional Requirements": 25,
            "Design Pattern Implementation": 20,
            "Code Quality and Style": 15,
            "Error Handling": 10,
            "Testing": 10,
            "SOLID Principles": 15,
            "Documentation": 5,
        }

    def _generate_advanced_rubric(self, _template: TaskTemplate) -> dict[str, int]:
        """Generate grading rubric for advanced level"""
        return {
            "Architecture and Design": 25,
            "Implementation Quality": 20,
            "Performance and Scalability": 15,
            "Error Handling and Resilience": 10,
            "Security Considerations": 10,
            "Testing and Quality Assurance": 15,
            "Innovation and Best Practices": 5,
        }

    def _generate_beginner_resources(self, _template: TaskTemplate) -> list[str]:
        """Generate learning resources for beginners"""
        return [
            "📖 SOLID Principles Guide - Section 1: Introduction",
            "🎥 Video: What is Single Responsibility Principle?",
            "💡 Tutorial: Basic Class Design in Python",
            "🔍 Code Examples: Simple SRP Examples",
            "📝 Cheat Sheet: Python Class Basics",
        ]

    def _generate_intermediate_resources(self, _template: TaskTemplate) -> list[str]:
        """Generate learning resources for intermediate level"""
        return [
            "📖 Clean Code - Chapter 10: Classes",
            "🎥 Video: Dependency Injection Patterns",
            "💡 Article: Interface Segregation in Practice",
            "🔍 Case Study: Refactoring Legacy Code",
            "📝 Best Practices: Error Handling in Python",
        ]

    def _generate_advanced_resources(self, _template: TaskTemplate) -> list[str]:
        """Generate learning resources for advanced level"""
        return [
            "📖 Clean Architecture - Robert Martin",
            "🎥 Conference Talk: Enterprise Architecture Patterns",
            "💡 Research Paper: Scalable System Design",
            "🔍 Open Source Study: Well-Architected Systems",
            "📝 Industry Report: Performance Optimization Techniques",
            "🏗️ Framework Documentation: FastAPI/Django Advanced Patterns",
        ]

    # Additional helper methods would be similar...
    def _generate_beginner_solution_template(self, template: TaskTemplate) -> str:
        """
        Generate detailed solution template for beginner level with extensive comments.

        Provides complete solution structure with:
        - Step-by-step implementation guide
        - Detailed code comments explaining each section
        - Example code snippets
        - Best practices explanations
        """
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Beginner Level Solution: SRP Refactoring Exercise
Complete solution with detailed explanations
"""

from typing import Optional

# ============================================================================
# STEP 1: UserValidator - Handles all user data validation
# ============================================================================
class UserValidator:
    """
    Validates user data according to business rules.
    Single Responsibility: Only validation logic.
    """

    def validate_user_data(self, user_data: dict) -> bool:
        """
        Validates user data for registration.

        Args:
            user_data (dict): Dictionary with 'username', 'email', 'password'

        Returns:
            bool: True if all validations pass, False otherwise
        """
        # Check username length (minimum 3 characters)
        username = user_data.get('username', '')
        if len(username) < 3:
            return False

        # Check email format (must contain @ symbol)
        email = user_data.get('email', '')
        if '@' not in email:
            return False

        # Check password strength (minimum 8 characters)
        password = user_data.get('password', '')
        if len(password) < 8:
            return False

        return True


# ============================================================================
# STEP 2: UserRepository - Handles all data persistence
# ============================================================================
class UserRepository:
    """
    Manages user data storage and retrieval.
    Single Responsibility: Only data access operations.
    """

    def __init__(self):
        """Initialize in-memory storage for demonstration"""
        self._users = {}  # In production, this would be a database

    def save_user(self, user: 'User') -> 'User':
        """
        Saves user to storage.

        Args:
            user: User object to save

        Returns:
            User: Saved user object
        """
        self._users[user.username] = user
        return user

    def find_by_username(self, username: str) -> Optional['User']:
        """
        Finds user by username.

        Args:
            username (str): Username to search for

        Returns:
            User or None: Found user or None if not found
        """
        return self._users.get(username)


# ============================================================================
# STEP 3: EmailService - Handles all email operations
# ============================================================================
class EmailService:
    """
    Manages email sending operations.
    Single Responsibility: Only email communication.
    """

    def send_welcome_email(self, user: 'User') -> bool:
        """
        Sends welcome email to new user.

        Args:
            user: User object to send email to

        Returns:
            bool: True if sent successfully
        """
        # In production, this would send actual email
        print(f"📧 Welcome email sent to {user.email}")
        return True


# ============================================================================
# STEP 4: User Domain Model - Represents user entity
# ============================================================================
class User:
    """
    Domain model representing a user.
    Single Responsibility: Only user data representation.
    """

    def __init__(self, username: str, email: str, password: str):
        """
        Initialize user with provided data.

        Args:
            username (str): User's username
            email (str): User's email address
            password (str): User's password (should be hashed in production)
        """
        self.username = username
        self.email = email
        self.password = password  # In production, store hashed password

    def __str__(self) -> str:
        """String representation of user"""
        return f"User(username='{self.username}', email='{self.email}')"


# ============================================================================
# STEP 5: UserService - Orchestrates business logic
# ============================================================================
class UserService:
    """
    Orchestrates user-related business operations.
    Single Responsibility: Only business logic coordination.

    Uses dependency injection to follow Dependency Inversion Principle.
    """

    def __init__(self, validator: UserValidator, repository: UserRepository,
                 email_service: EmailService):
        """
        Initialize service with dependencies.

        Args:
            validator: UserValidator instance for validation
            repository: UserRepository instance for data access
            email_service: EmailService instance for email operations
        """
        self.validator = validator
        self.repository = repository
        self.email_service = email_service

    def create_user(self, user_data: dict) -> User:
        """
        Creates a new user following the complete workflow.

        Args:
            user_data (dict): User data dictionary

        Returns:
            User: Created user object

        Raises:
            ValueError: If validation fails
        """
        # Step 1: Validate user data
        if not self.validator.validate_user_data(user_data):
            raise ValueError("Invalid user data")

        # Step 2: Create User domain object
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )

        # Step 3: Save user to repository
        saved_user = self.repository.save_user(user)

        # Step 4: Send welcome email
        self.email_service.send_welcome_email(saved_user)

        # Step 5: Return created user
        return saved_user


# ============================================================================
# STEP 6: Demonstration - Shows dependency injection in action
# ============================================================================
def main():
    """Demonstrates the refactored system with dependency injection"""
    # Create dependencies
    validator = UserValidator()
    repository = UserRepository()
    email_service = EmailService()

    # Create UserService with injected dependencies
    user_service = UserService(validator, repository, email_service)

    # Test user creation
    try:
        user_data = {
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'securepass123'
        }
        user = user_service.create_user(user_data)
        print(f"✅ User created successfully: {user}")
    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
'''

        # Generic template for other tasks
        return f'''#!/usr/bin/env python3
"""
Beginner Level Solution Template: {template.title}
Module: {template.module}

This solution provides a complete implementation with detailed explanations.
Each section includes:
- Clear comments explaining the purpose
- Step-by-step implementation guide
- Best practices and patterns used
"""

from typing import Optional

# ============================================================================
# SOLUTION STRUCTURE
# ============================================================================
# TODO: Replace this template with actual solution for {template.id}
#
# Recommended structure:
# 1. Import necessary modules
# 2. Define data models/classes
# 3. Implement core functionality with detailed comments
# 4. Add error handling
# 5. Include example usage
# ============================================================================

# Example structure (replace with actual implementation):
def solution_function():
    """
    Main solution function with detailed documentation.

    Steps:
    1. [Step 1 description]
    2. [Step 2 description]
    3. [Step 3 description]
    """
    # Step 1: [Detailed explanation]
    pass

    # Step 2: [Detailed explanation]
    pass

    # Step 3: [Detailed explanation]
    pass


if __name__ == "__main__":
    # Example usage with comments
    solution_function()
'''

    def _generate_intermediate_solution_template(self, template: TaskTemplate) -> str:
        """
        Generate solution template for intermediate level with moderate guidance.

        Provides solution structure with:
        - Key implementation sections
        - Moderate code comments
        - Design pattern hints
        - Some implementation guidance
        """
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Intermediate Level Solution: SRP Refactoring Exercise
Solution with moderate guidance and design pattern hints
"""

class UserValidator:
    """Validates user data - follows SRP"""

    def validate_user_data(self, user_data: dict) -> bool:
        """Validate username, email, and password"""
        if len(user_data.get('username', '')) < 3:
            return False
        if '@' not in user_data.get('email', ''):
            return False
        if len(user_data.get('password', '')) < 8:
            return False
        return True


class UserRepository:
    """Manages user data persistence - follows SRP"""

    def __init__(self):
        self._users = {}

    def save_user(self, user: 'User') -> 'User':
        """Save user to storage"""
        self._users[user.username] = user
        return user

    def find_by_username(self, username: str) -> Optional['User']:
        """Find user by username"""
        return self._users.get(username)


class EmailService:
    """Handles email operations - follows SRP"""

    def send_welcome_email(self, user: 'User') -> bool:
        """Send welcome email"""
        print(f"📧 Welcome email sent to {user.email}")
        return True


class User:
    """User domain model"""

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}')"


class UserService:
    """Orchestrates user business logic - uses dependency injection"""

    def __init__(self, validator: UserValidator, repository: UserRepository,
                 email_service: EmailService):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service

    def create_user(self, user_data: dict) -> User:
        """Create user following validation -> save -> notify workflow"""
        if not self.validator.validate_user_data(user_data):
            raise ValueError("Invalid user data")

        user = User(user_data['username'], user_data['email'], user_data['password'])
        saved_user = self.repository.save_user(user)
        self.email_service.send_welcome_email(saved_user)
        return saved_user


def main():
    """Demonstrate dependency injection"""
    validator = UserValidator()
    repository = UserRepository()
    email_service = EmailService()
    user_service = UserService(validator, repository, email_service)

    user_data = {
        'username': 'johndoe',
        'email': 'john@example.com',
        'password': 'securepass123'
    }
    user = user_service.create_user(user_data)
    print(f"✅ User created: {user}")


if __name__ == "__main__":
    main()
'''

        # Generic template for other tasks
        return f'''#!/usr/bin/env python3
"""
Intermediate Level Solution Template: {template.title}
Module: {template.module}

Solution structure with moderate guidance.
Key sections and design patterns are indicated.
"""

# Core implementation
# - Consider design patterns: Strategy, Factory, Observer
# - Implement error handling
# - Follow SOLID principles
# - Add appropriate type hints

def solution_function():
    """Main solution - implement core logic"""
    # Implementation with moderate comments
    pass


if __name__ == "__main__":
    solution_function()
'''

    def _generate_advanced_solution_template(self, template: TaskTemplate) -> str:
        """
        Generate minimal solution template for advanced level.

        Provides minimal structure with:
        - Basic code outline
        - Architectural hints
        - Design pattern suggestions
        - Requires independent implementation
        """
        if template.id == "srp_refactoring":
            return '''#!/usr/bin/env python3
"""
Advanced Level Solution: SRP Refactoring Exercise
Minimal outline - implement complete solution independently
"""

from typing import Optional

# Implement complete solution following SRP
# Consider: error handling, logging, configuration, testing
# Apply: dependency injection, interface segregation
# Extend: add additional features (user updates, deletion, etc.)


class UserValidator:
    def validate_user_data(self, user_data: dict) -> bool:
        # Implement validation with comprehensive rules
        pass


class UserRepository:
    def __init__(self):
        # Consider: database connection, connection pooling
        pass

    def save_user(self, user: 'User') -> 'User':
        # Implement with transaction handling
        pass

    def find_by_username(self, username: str) -> Optional['User']:
        pass


class EmailService:
    def send_welcome_email(self, user: 'User') -> bool:
        # Implement with retry logic, error handling
        pass


class User:
    def __init__(self, username: str, email: str, password: str):
        # Consider: password hashing, validation
        pass


class UserService:
    def __init__(self, validator: UserValidator, repository: UserRepository,
                 email_service: EmailService):
        # Implement dependency injection
        pass

    def create_user(self, user_data: dict) -> User:
        # Implement with full error handling and logging
        pass


# Extend with additional features:
# - User update functionality
# - User deletion
# - User query/search
# - Batch operations
# - Caching layer
# - Event publishing
'''

        # Generic template for other tasks
        return f'''#!/usr/bin/env python3
"""
Advanced Level Solution Template: {template.title}
Module: {template.module}

Minimal outline - implement complete solution independently.
Consider: architecture, design patterns, error handling, testing, scalability.
"""

# Implement complete solution
# - Apply appropriate design patterns
# - Consider architectural concerns
# - Implement comprehensive error handling
# - Add logging and monitoring
# - Consider performance and scalability
# - Extend with additional features

def solution_function():
    """Implement complete solution"""
    pass


if __name__ == "__main__":
    solution_function()
'''


# =============================================================================
# ADAPTIVE LEARNING SYSTEM
# =============================================================================


class ProgressTracker:
    """Track student progress and recommend difficulty levels"""

    def __init__(self):
        self.students: dict[str, StudentProgress] = {}

    def get_student_progress(self, student_id: str) -> StudentProgress:
        """Get or create student progress"""
        if student_id not in self.students:
            self.students[student_id] = StudentProgress(student_id)
        return self.students[student_id]

    def record_task_completion(
        self,
        student_id: str,
        task_id: str,
        score: float,
        max_score: float,
        time_taken: int,
        difficulty: DifficultyLevel,
    ):
        """Record task completion"""
        progress = self.get_student_progress(student_id)

        # Calculate percentage safely, guarding against zero or negative max_score
        percentage = 0.0 if max_score <= 0 else score / max_score * 100

        performance = {
            "task_id": task_id,
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "time_taken": time_taken,
            "difficulty": difficulty.value,
            "timestamp": datetime.now().isoformat(),
        }

        progress.performance_history.append(performance)
        progress.completed_tasks.append(task_id)

        # Update skill levels based on performance
        self._update_skill_levels(progress, performance)

        # Update level recommendations
        self._update_level_recommendations(progress)

    def _update_skill_levels(
        self, progress: StudentProgress, performance: dict[str, Any]
    ):
        """Update skill levels based on performance"""
        percentage = performance["percentage"]
        difficulty = DifficultyLevel(performance["difficulty"])

        # Determine which skills to update (simplified logic)
        task_id = performance["task_id"]
        if "srp" in task_id or "solid" in task_id:
            domain = SkillDomain.SOLID_PRINCIPLES
        elif "pattern" in task_id:
            domain = SkillDomain.DESIGN_PATTERNS
        elif "architecture" in task_id:
            domain = SkillDomain.ARCHITECTURE
        else:
            domain = SkillDomain.SOLID_PRINCIPLES  # Default

        # Update skill level
        current_level = progress.skill_levels[domain]

        if percentage >= 90:
            # Excellent performance - increase skill level
            if difficulty == DifficultyLevel.ADVANCED:
                progress.skill_levels[domain] = min(10, current_level + 2)
            elif difficulty == DifficultyLevel.INTERMEDIATE:
                progress.skill_levels[domain] = min(10, current_level + 1)
            else:  # BEGINNER
                progress.skill_levels[domain] = min(10, current_level + 1)
        elif percentage >= 70:
            # Good performance - slight increase or maintain
            if difficulty != DifficultyLevel.BEGINNER:
                progress.skill_levels[domain] = min(10, current_level + 1)
        elif percentage < 50 and current_level > 1:
            # Poor performance - might need to decrease level
            progress.skill_levels[domain] = max(1, current_level - 1)

    def _update_level_recommendations(self, progress: StudentProgress):
        """Update difficulty level recommendations"""
        for domain in SkillDomain:
            skill_level = progress.skill_levels[domain]

            if skill_level <= 3:
                recommended = DifficultyLevel.BEGINNER
            elif skill_level <= 7:
                recommended = DifficultyLevel.INTERMEDIATE
            else:
                recommended = DifficultyLevel.ADVANCED

            progress.current_level_recommendations[domain.value] = recommended

    def recommend_difficulty(
        self, student_id: str, task_template: TaskTemplate
    ) -> DifficultyLevel:
        """Recommend difficulty level for a specific task"""
        progress = self.get_student_progress(student_id)

        # Get relevant skill domains for the task (simplified)
        if task_template.module == "SOLID":
            domain = SkillDomain.SOLID_PRINCIPLES
        elif task_template.module == "Patterns":
            domain = SkillDomain.DESIGN_PATTERNS
        elif task_template.module == "Architecture":
            domain = SkillDomain.ARCHITECTURE
        else:
            domain = SkillDomain.SOLID_PRINCIPLES

        return progress.current_level_recommendations.get(
            domain.value, DifficultyLevel.BEGINNER
        )

    def get_progress_summary(self, student_id: str) -> dict[str, Any]:
        """Get comprehensive progress summary"""
        progress = self.get_student_progress(student_id)

        # Calculate statistics
        total_tasks = len(progress.completed_tasks)
        recent_performance = (
            progress.performance_history[-5:] if progress.performance_history else []
        )
        avg_recent_score = (
            sum(p["percentage"] for p in recent_performance) / len(recent_performance)
            if recent_performance
            else 0
        )

        return {
            "student_id": student_id,
            "total_tasks_completed": total_tasks,
            "skill_levels": dict(progress.skill_levels),
            "current_recommendations": dict(progress.current_level_recommendations),
            "average_recent_performance": round(avg_recent_score, 2),
            "performance_trend": self._calculate_trend(progress.performance_history),
            "suggested_next_topics": self._suggest_next_topics(progress),
        }

    def _calculate_trend(self, performance_history: list[dict[str, Any]]) -> str:
        """Calculate performance trend"""
        if len(performance_history) < 3:
            return "insufficient_data"

        recent_scores = [p["percentage"] for p in performance_history[-5:]]
        earlier_scores = (
            [p["percentage"] for p in performance_history[-10:-5]]
            if len(performance_history) >= 10
            else recent_scores
        )

        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)

        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "declining"
        else:
            return "stable"

    def _suggest_next_topics(self, progress: StudentProgress) -> list[str]:
        """Suggest next topics based on progress"""
        suggestions = []

        for domain, level in progress.skill_levels.items():
            if level < 5:
                suggestions.append(
                    f"Focus on {domain.value.replace('_', ' ').title()} fundamentals"
                )
            elif level < 8:
                suggestions.append(
                    f"Advanced {domain.value.replace('_', ' ').title()} patterns"
                )

        return suggestions[:3]  # Return top 3 suggestions


# =============================================================================
# TASK TEMPLATES LIBRARY
# =============================================================================


class TaskLibrary:
    """Library of task templates for different modules"""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> dict[str, TaskTemplate]:
        """Initialize task templates"""
        return {
            "srp_refactoring": TaskTemplate(
                id="srp_refactoring",
                title="User Service SRP Refactoring",
                description="Refactor a monolithic UserService class to follow Single Responsibility Principle by separating validation, persistence, and notification concerns.",
                module="SOLID",
                base_objectives=[
                    LearningObjective(
                        "Apply Single Responsibility Principle",
                        [
                            SkillRequirement(
                                SkillDomain.SOLID_PRINCIPLES, 5, "SRP Understanding"
                            )
                        ],
                        [
                            "Separate concerns properly",
                            "Create focused classes",
                            "Implement dependency injection",
                        ],
                    )
                ],
                estimated_time_minutes={
                    DifficultyLevel.BEGINNER: 120,
                    DifficultyLevel.INTERMEDIATE: 90,
                    DifficultyLevel.ADVANCED: 180,
                },
                prerequisites=["Basic Python", "Class Design"],
            ),
            "ecommerce_patterns": TaskTemplate(
                id="ecommerce_patterns",
                title="E-commerce System with Design Patterns",
                description="Build a complete e-commerce system applying multiple design patterns for payment processing, notifications, order management, and enhancements.",
                module="Patterns",
                base_objectives=[
                    LearningObjective(
                        "Apply Multiple Design Patterns",
                        [
                            SkillRequirement(
                                SkillDomain.DESIGN_PATTERNS, 6, "Strategy Pattern"
                            ),
                            SkillRequirement(
                                SkillDomain.DESIGN_PATTERNS, 6, "Observer Pattern"
                            ),
                            SkillRequirement(
                                SkillDomain.DESIGN_PATTERNS, 5, "Factory Pattern"
                            ),
                        ],
                        [
                            "Implement Strategy pattern",
                            "Create Observer system",
                            "Build Factory classes",
                        ],
                    )
                ],
                estimated_time_minutes={
                    DifficultyLevel.BEGINNER: 240,
                    DifficultyLevel.INTERMEDIATE: 180,
                    DifficultyLevel.ADVANCED: 360,
                },
                prerequisites=["SOLID Principles", "Basic Design Patterns"],
            ),
            "blog_platform": TaskTemplate(
                id="blog_platform",
                title="Blog Platform Monolithic Architecture",
                description="Create a blog platform following clean monolithic architecture principles with proper layering, domain modeling, and API design.",
                module="Architecture",
                base_objectives=[
                    LearningObjective(
                        "Design Clean Monolithic Architecture",
                        [
                            SkillRequirement(
                                SkillDomain.ARCHITECTURE, 7, "Clean Architecture"
                            ),
                            SkillRequirement(
                                SkillDomain.DOMAIN_DRIVEN_DESIGN, 5, "Domain Modeling"
                            ),
                        ],
                        [
                            "Create layered architecture",
                            "Implement repository pattern",
                            "Design clean APIs",
                        ],
                    )
                ],
                estimated_time_minutes={
                    DifficultyLevel.BEGINNER: 360,
                    DifficultyLevel.INTERMEDIATE: 300,
                    DifficultyLevel.ADVANCED: 480,
                },
                prerequisites=[
                    "Design Patterns",
                    "Web Development Basics",
                    "Database Design",
                ],
            ),
        }

    def get_template(self, template_id: str) -> TaskTemplate | None:
        """Get task template by ID"""
        return self.templates.get(template_id)

    def list_templates(self) -> list[TaskTemplate]:
        """List all available templates"""
        return list(self.templates.values())

    def get_templates_by_module(self, module: str) -> list[TaskTemplate]:
        """Get templates for specific module"""
        return [t for t in self.templates.values() if t.module == module]


# =============================================================================
# MAIN INTERFACE
# =============================================================================


class AdaptiveLearningSystem:
    """Main interface for the adaptive learning system"""

    def __init__(self):
        self.task_library = TaskLibrary()
        self.progress_tracker = ProgressTracker()
        self.task_generator = TaskGenerator()

    def get_personalized_task(
        self, student_id: str, template_id: str
    ) -> ProgrammingTask:
        """Get personalized task for student"""
        template = self.task_library.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Get recommended difficulty
        recommended_difficulty = self.progress_tracker.recommend_difficulty(
            student_id, template
        )

        # Generate task
        task = template.generate_task(recommended_difficulty)

        print(
            f"📚 Generated {recommended_difficulty.value} level task for student {student_id}"
        )
        print(f"⏱️  Estimated time: {task.estimated_time} minutes")

        return task

    def submit_task_result(
        self,
        student_id: str,
        task_id: str,
        score: float,
        max_score: float,
        time_taken: int,
        difficulty: DifficultyLevel,
    ):
        """Submit task completion result"""
        self.progress_tracker.record_task_completion(
            student_id, task_id, score, max_score, time_taken, difficulty
        )

    def get_student_dashboard(self, student_id: str) -> dict[str, Any]:
        """Get student dashboard with progress and recommendations"""
        return self.progress_tracker.get_progress_summary(student_id)

    def recommend_next_task(self, student_id: str) -> str | None:
        """Recommend next task for student"""
        progress = self.progress_tracker.get_student_progress(student_id)

        # Find uncompleted tasks
        completed = set(progress.completed_tasks)
        all_templates = self.task_library.list_templates()

        for template in all_templates:
            if template.id not in completed and self._check_prerequisites(
                student_id, template
            ):
                return template.id

        return None

    def _check_prerequisites(self, student_id: str, template: TaskTemplate) -> bool:
        """Check if student meets prerequisites"""
        progress = self.progress_tracker.get_student_progress(student_id)

        # Simplified prerequisite checking
        if (
            template.module == "Patterns"
            and "srp_refactoring" not in progress.completed_tasks
        ):
            return False

        return not (
            template.module == "Architecture" and len(progress.completed_tasks) < 2
        )


# =============================================================================
# DEMONSTRATION AND CLI
# =============================================================================


def demo_adaptive_system():
    """Demonstrate the adaptive learning system"""
    print("🎓 Adaptive Learning System Demo")
    print("=" * 50)

    system = AdaptiveLearningSystem()

    # Simulate student learning journey
    student_id = "student_001"

    print(f"\n👨‍🎓 Student: {student_id}")
    print("Initial dashboard:")
    dashboard = system.get_student_dashboard(student_id)
    print(json.dumps(dashboard, indent=2))

    # Get first task
    print("\n📝 Getting personalized task...")
    task = system.get_personalized_task(student_id, "srp_refactoring")

    print(f"Title: {task.title}")
    print(f"Difficulty: {task.difficulty.value}")
    print(f"Estimated time: {task.estimated_time} minutes")
    print(f"Instructions ({len(task.instructions)} steps):")
    for i, instruction in enumerate(task.instructions[:3], 1):
        print(f"  {i}. {instruction}")
    if len(task.instructions) > 3:
        print(f"  ... and {len(task.instructions) - 3} more steps")

    # Simulate task completion
    print("\n✅ Simulating task completion...")
    system.submit_task_result(
        student_id, "srp_refactoring", 85, 100, 110, task.difficulty
    )

    # Updated dashboard
    print("\n📊 Updated dashboard:")
    dashboard = system.get_student_dashboard(student_id)
    print(json.dumps(dashboard, indent=2))

    # Recommend next task
    next_task = system.recommend_next_task(student_id)
    print(f"\n🎯 Recommended next task: {next_task}")

    # Show how difficulty adapts
    print("\n🔄 Getting next task (difficulty should adapt)...")
    if next_task:
        next_task_obj = system.get_personalized_task(student_id, next_task)
        print(f"Next task difficulty: {next_task_obj.difficulty.value}")


def main():
    """
    Main CLI interface for the difficulty system.

    💡 Простыми словами: Это командная строка для работы с системой заданий.
    Как меню в ресторане - выбираете, что хотите получить.

    Usage Examples:
        # Получить задание для студента (автоматический уровень)
        python difficulty_system.py --student student_001 --task srp_refactoring

        # Принудительно установить уровень сложности
        python difficulty_system.py --student student_001 --task srp_refactoring --level beginner

        # Посмотреть прогресс студента
        python difficulty_system.py --student student_001

        # Посмотреть все доступные задания
        python difficulty_system.py

        # Запустить демо
        python difficulty_system.py --demo

    Commands:
        --student ID      : ID студента
        --task TASK_ID    : ID задания (например, srp_refactoring)
        --level LEVEL     : Уровень сложности (beginner/intermediate/advanced)
        --demo            : Запустить демонстрацию системы
    """
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive Learning System")
    parser.add_argument("--demo", help="Run demonstration", action="store_true")
    parser.add_argument("--student", help="Student ID")
    parser.add_argument("--task", help="Task template ID")
    parser.add_argument(
        "--level",
        help="Force specific difficulty level",
        choices=["beginner", "intermediate", "advanced"],
    )

    args = parser.parse_args()

    if args.demo:
        demo_adaptive_system()
        return

    system = AdaptiveLearningSystem()

    if args.student and args.task:
        # Generate task for student
        if args.level:
            # Force specific level
            template = system.task_library.get_template(args.task)
            if template:
                difficulty = DifficultyLevel(args.level)
                task = template.generate_task(difficulty)

                print(f"📝 {task.title}")
                print(f"🎯 Difficulty: {task.difficulty.value}")
                print(f"📊 Estimated time: {task.estimated_time} minutes")
                print("\nInstructions:")
                for i, instruction in enumerate(task.instructions, 1):
                    print(f"{i}. {instruction}")
            else:
                print(f"❌ Task template not found: {args.task}")
        else:
            # Use adaptive difficulty
            task = system.get_personalized_task(args.student, args.task)
            print(f"📝 Generated adaptive task: {task.title}")

    elif args.student:
        # Show student dashboard
        dashboard = system.get_student_dashboard(args.student)
        print(f"📊 Dashboard for {args.student}:")
        print(json.dumps(dashboard, indent=2))

    else:
        # Show available templates
        print("📚 Available Task Templates:")
        for template in system.task_library.list_templates():
            print(f"  • {template.id}: {template.title}")
            print(f"    Module: {template.module}")
            print(
                f"    Time: {template.estimated_time_minutes[DifficultyLevel.INTERMEDIATE]} min (intermediate)"
            )


if __name__ == "__main__":
    main()
