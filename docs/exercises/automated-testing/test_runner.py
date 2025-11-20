#!/usr/bin/env python3
"""
Automated Testing System for Student Solutions
Module: All Modules - Comprehensive Testing Framework

This system provides automated testing capabilities for validating
student solutions across all course modules, including:
- Unit testing for individual components
- Integration testing for complete systems
- Code quality analysis
- Pattern recognition validation
- Architecture compliance checking
"""

import os
import sys
import ast
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import inspect


# =============================================================================
# TEST FRAMEWORK CORE
# =============================================================================


class TestResult(Enum):
    """Test result enumeration"""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"


@dataclass
class TestCase:
    """Individual test case definition"""

    name: str
    description: str
    test_function: Callable
    module: str
    points: int = 1
    timeout: int = 30
    required_patterns: List[str] = field(default_factory=list)
    required_classes: List[str] = field(default_factory=list)
    required_methods: List[str] = field(default_factory=list)


@dataclass
class TestExecutionResult:
    """Result of test execution"""

    test_case: TestCase
    result: TestResult
    execution_time: float
    error_message: str = ""
    output: str = ""
    score: float = 0.0


@dataclass
class ModuleTestSuite:
    """Test suite for a complete module"""

    module_name: str
    test_cases: List[TestCase] = field(default_factory=list)
    max_points: int = 0

    def __post_init__(self):
        self.max_points = sum(case.points for case in self.test_cases)


# =============================================================================
# CODE ANALYSIS UTILITIES
# =============================================================================


class CodeAnalyzer:
    """
    Utility for analyzing Python code structure.

    💡 Простыми словами: Это "детектив" для кода - он изучает ваш код и находит:
    - Какие классы вы создали
    - Какие методы есть
    - Какие паттерны использованы
    - Есть ли ошибки в структуре

    Example:
        >>> analyzer = CodeAnalyzer()
        >>> code = "class User: pass"
        >>> tree = analyzer.parse_code(code)
        >>> classes = analyzer.find_classes(tree)
        >>> print(classes)
        ['User']
    """

    @staticmethod
    def parse_code(code_content: str) -> Optional[ast.AST]:
        """
        Parse Python code into AST (Abstract Syntax Tree).

        💡 Простыми словами: Превращает ваш код в "дерево" - структуру,
        которую компьютер может анализировать. Как парсер предложения в грамматике.

        Args:
            code_content: Строка с Python кодом

        Returns:
            AST объект или None, если есть синтаксические ошибки

        Example:
            >>> code = '''
            ... class User:
            ...     def __init__(self, name):
            ...         self.name = name
            ... '''
            >>> tree = CodeAnalyzer.parse_code(code)
            >>> if tree:
            ...     print("✅ Code is valid!")
        """
        try:
            return ast.parse(code_content)
        except SyntaxError as e:
            print(f"❌ Syntax error in code: {e}")
            print("💡 Tip: Check your Python syntax. Common errors:")
            print("   - Missing colons (:) after if/for/def/class")
            print("   - Incorrect indentation")
            print("   - Missing parentheses or brackets")
            return None

    @staticmethod
    def find_classes(tree: ast.AST) -> List[str]:
        """Find all class names in AST"""

        class ClassVisitor(ast.NodeVisitor):
            def __init__(self):
                self.classes = []

            def visit_ClassDef(self, node):
                self.classes.append(node.name)
                self.generic_visit(node)

        visitor = ClassVisitor()
        visitor.visit(tree)
        return visitor.classes

    @staticmethod
    def find_methods(tree: ast.AST, class_name: Optional[str] = None) -> List[str]:
        """Find all method names, optionally within a specific class"""

        class MethodVisitor(ast.NodeVisitor):
            def __init__(self, target_class=None):
                self.methods = []
                self.target_class = target_class
                self.current_class = None

            def visit_ClassDef(self, node):
                old_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = old_class

            def visit_FunctionDef(self, node):
                if self.target_class is None or self.current_class == self.target_class:
                    self.methods.append(node.name)
                self.generic_visit(node)

        visitor = MethodVisitor(class_name)
        visitor.visit(tree)
        return visitor.methods

    @staticmethod
    def find_design_patterns(tree: ast.AST) -> Dict[str, bool]:
        """Detect design patterns in code"""
        patterns = {
            "singleton": False,
            "factory": False,
            "strategy": False,
            "observer": False,
            "decorator": False,
            "command": False,
            "builder": False,
        }

        class PatternVisitor(ast.NodeVisitor):
            def __init__(self):
                self.class_names = []
                self.method_names = []
                self.has_abstract_methods = False
                self.has_inheritance = False

            def visit_ClassDef(self, node):
                self.class_names.append(node.name.lower())

                # Check for inheritance
                if node.bases:
                    self.has_inheritance = True

                # Check for abstract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            if (
                                isinstance(decorator, ast.Name)
                                and decorator.id == "abstractmethod"
                            ):
                                self.has_abstract_methods = True

                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                self.method_names.append(node.name.lower())
                self.generic_visit(node)

        visitor = PatternVisitor()
        visitor.visit(tree)

        # Pattern detection logic
        class_names = " ".join(visitor.class_names)
        method_names = " ".join(visitor.method_names)

        # Singleton pattern
        if "singleton" in class_names or "_instance" in method_names:
            patterns["singleton"] = True

        # Factory pattern
        if (
            "factory" in class_names
            or "create" in method_names
            or "make" in method_names
        ):
            patterns["factory"] = True

        # Strategy pattern
        if (
            visitor.has_abstract_methods
            and visitor.has_inheritance
            and "strategy" in class_names
        ):
            patterns["strategy"] = True

        # Observer pattern
        if (
            "observer" in class_names
            or "notify" in method_names
            or "subscribe" in method_names
        ):
            patterns["observer"] = True

        # Decorator pattern
        if "decorator" in class_names or "wrap" in method_names:
            patterns["decorator"] = True

        # Command pattern
        if "command" in class_names and "execute" in method_names:
            patterns["command"] = True

        # Builder pattern
        if "builder" in class_names or "build" in method_names:
            patterns["builder"] = True

        return patterns


class SolutionImporter:
    """Utility for safely importing student solutions"""

    @staticmethod
    def import_solution(file_path: str, module_name: str = "student_solution"):
        """Safely import a Python file as a module"""
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                raise ImportError(f"Could not load spec from {file_path}")

            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise ImportError(
                    f"Could not load module from {file_path}: loader is None"
                )
            spec.loader.exec_module(module)
            return module

        except Exception as e:
            print(f"❌ Error importing {file_path}: {e}")
            return None


# =============================================================================
# MODULE-SPECIFIC TEST SUITES
# =============================================================================


class SOLIDTestSuite:
    """Test suite for SOLID principles module"""

    @staticmethod
    def create_srp_tests() -> List[TestCase]:
        """Create tests for Single Responsibility Principle"""

        def test_user_validator_exists(solution):
            """Test that UserValidator class exists"""
            assert hasattr(solution, "UserValidator"), "UserValidator class not found"
            validator = solution.UserValidator()
            assert hasattr(validator, "validate_user_data"), (
                "validate_user_data method not found"
            )

        def test_user_repository_exists(solution):
            """Test that UserRepository class exists"""
            assert hasattr(solution, "UserRepository"), "UserRepository class not found"
            repo = solution.UserRepository()
            assert hasattr(repo, "save_user"), "save_user method not found"

        def test_email_service_exists(solution):
            """Test that EmailService class exists"""
            assert hasattr(solution, "EmailService"), "EmailService class not found"
            service = solution.EmailService()
            assert hasattr(service, "send_welcome_email"), (
                "send_welcome_email method not found"
            )

        def test_user_service_srp_compliance(solution):
            """Test that UserService follows SRP"""
            assert hasattr(solution, "UserService"), "UserService class not found"

            # UserService should not directly handle validation, persistence, or email
            user_service_methods = dir(solution.UserService)

            # Check that validation is delegated
            assert "validate_user_data" not in user_service_methods, (
                "UserService should delegate validation to UserValidator"
            )

            # Check that email sending is delegated
            assert "send_email" not in user_service_methods, (
                "UserService should delegate email sending to EmailService"
            )

        def test_dependency_injection(solution):
            """Test that dependencies are properly injected"""
            assert hasattr(solution, "UserService"), "UserService class not found"

            # Check constructor parameters
            init_signature = inspect.signature(solution.UserService.__init__)
            param_names = list(init_signature.parameters.keys())

            expected_deps = ["validator", "repository", "email_service"]
            for dep in expected_deps:
                assert dep in param_names, (
                    f"UserService should accept {dep} as dependency"
                )

        return [
            TestCase(
                "test_user_validator_exists",
                "UserValidator class exists",
                test_user_validator_exists,
                "SOLID-SRP",
                2,
                required_classes=["UserValidator"],
            ),
            TestCase(
                "test_user_repository_exists",
                "UserRepository class exists",
                test_user_repository_exists,
                "SOLID-SRP",
                2,
                required_classes=["UserRepository"],
            ),
            TestCase(
                "test_email_service_exists",
                "EmailService class exists",
                test_email_service_exists,
                "SOLID-SRP",
                2,
                required_classes=["EmailService"],
            ),
            TestCase(
                "test_user_service_srp_compliance",
                "UserService follows SRP",
                test_user_service_srp_compliance,
                "SOLID-SRP",
                3,
            ),
            TestCase(
                "test_dependency_injection",
                "Proper dependency injection",
                test_dependency_injection,
                "SOLID-SRP",
                3,
            ),
        ]


class DesignPatternsTestSuite:
    """Test suite for Design Patterns module"""

    @staticmethod
    def create_pattern_tests() -> List[TestCase]:
        """Create tests for design patterns"""

        def test_strategy_pattern(solution):
            """Test Strategy pattern implementation"""
            # Look for payment strategies
            classes = [
                name
                for name in dir(solution)
                if "Payment" in name and "Strategy" in name
            ]
            assert len(classes) >= 2, (
                "At least 2 payment strategies should be implemented"
            )

            # Test that strategies have process_payment method
            for class_name in classes:
                if class_name != "PaymentStrategy":  # Skip abstract base
                    strategy_class = getattr(solution, class_name)
                    assert hasattr(strategy_class, "process_payment"), (
                        f"{class_name} should have process_payment method"
                    )

        def test_observer_pattern(solution):
            """Test Observer pattern implementation"""
            # Look for observer classes
            observer_classes = [
                name
                for name in dir(solution)
                if "Observer" in name or "Notifier" in name
            ]
            assert len(observer_classes) >= 2, (
                "At least 2 observer implementations should exist"
            )

            # Check for notification methods
            for class_name in observer_classes:
                if "Observer" not in class_name:  # Skip abstract base
                    observer_class = getattr(solution, class_name)
                    methods = dir(observer_class)
                    assert any("on_" in method for method in methods), (
                        f"{class_name} should have event handler methods"
                    )

        def test_factory_pattern(solution):
            """Test Factory pattern implementation"""
            # Look for factory classes
            factory_classes = [name for name in dir(solution) if "Factory" in name]
            assert len(factory_classes) >= 1, "At least 1 factory should be implemented"

            # Test factory methods
            for class_name in factory_classes:
                factory_class = getattr(solution, class_name)
                methods = dir(factory_class)
                assert any("create" in method.lower() for method in methods), (
                    f"{class_name} should have creation methods"
                )

        def test_command_pattern(solution):
            """Test Command pattern implementation"""
            # Look for command classes
            command_classes = [name for name in dir(solution) if "Command" in name]
            assert len(command_classes) >= 2, (
                "At least 2 command implementations should exist"
            )

            # Test command interface
            for class_name in command_classes:
                if "Command" in class_name and class_name != "OrderCommand":
                    command_class = getattr(solution, class_name)
                    assert hasattr(command_class, "execute"), (
                        f"{class_name} should have execute method"
                    )
                    assert hasattr(command_class, "undo"), (
                        f"{class_name} should have undo method"
                    )

        def test_decorator_pattern(solution):
            """Test Decorator pattern implementation"""
            # Look for decorator classes
            decorator_classes = [name for name in dir(solution) if "Decorator" in name]
            assert len(decorator_classes) >= 2, (
                "At least 2 decorator implementations should exist"
            )

            # Test decorator interface
            for class_name in decorator_classes:
                if class_name != "OrderDecorator":  # Skip abstract base
                    decorator_class = getattr(solution, class_name)
                    assert hasattr(decorator_class, "get_total_amount"), (
                        f"{class_name} should have get_total_amount method"
                    )

        return [
            TestCase(
                "test_strategy_pattern",
                "Strategy pattern implementation",
                test_strategy_pattern,
                "Patterns-Strategy",
                4,
                required_patterns=["strategy"],
            ),
            TestCase(
                "test_observer_pattern",
                "Observer pattern implementation",
                test_observer_pattern,
                "Patterns-Observer",
                4,
                required_patterns=["observer"],
            ),
            TestCase(
                "test_factory_pattern",
                "Factory pattern implementation",
                test_factory_pattern,
                "Patterns-Factory",
                3,
                required_patterns=["factory"],
            ),
            TestCase(
                "test_command_pattern",
                "Command pattern implementation",
                test_command_pattern,
                "Patterns-Command",
                4,
                required_patterns=["command"],
            ),
            TestCase(
                "test_decorator_pattern",
                "Decorator pattern implementation",
                test_decorator_pattern,
                "Patterns-Decorator",
                4,
                required_patterns=["decorator"],
            ),
        ]


class ArchitectureTestSuite:
    """Test suite for Architecture module"""

    @staticmethod
    def create_architecture_tests() -> List[TestCase]:
        """Create tests for architecture patterns"""

        def test_repository_pattern(solution):
            """Test Repository pattern implementation"""
            # Look for repository classes
            repo_classes = [name for name in dir(solution) if "Repository" in name]
            assert len(repo_classes) >= 2, (
                "At least 2 repository implementations should exist"
            )

            # Test repository interface
            for class_name in repo_classes:
                if "Repository" in class_name and not class_name.startswith("I"):
                    repo_class = getattr(solution, class_name)
                    assert hasattr(repo_class, "save"), (
                        f"{class_name} should have save method"
                    )
                    assert hasattr(repo_class, "find_by_id"), (
                        f"{class_name} should have find_by_id method"
                    )

        def test_service_layer(solution):
            """Test Service layer implementation"""
            service_classes = [name for name in dir(solution) if "Service" in name]
            assert len(service_classes) >= 2, (
                "At least 2 service implementations should exist"
            )

            # Services should not directly access database
            for class_name in service_classes:
                service_class = getattr(solution, class_name)
                methods = dir(service_class)

                # Check that services don't have direct database operations
                db_methods = ["execute", "query", "commit", "rollback"]
                for db_method in db_methods:
                    assert db_method not in methods, (
                        f"{class_name} should not have direct database method {db_method}"
                    )

        def test_domain_entities(solution):
            """Test Domain entities implementation"""
            # Look for domain entities
            entity_classes = [
                name
                for name in dir(solution)
                if any(entity in name for entity in ["User", "Article", "Comment"])
            ]
            assert len(entity_classes) >= 3, (
                "Should have User, Article, and Comment entities"
            )

            # Test entity behavior
            if hasattr(solution, "User"):
                user_class = solution.User
                assert hasattr(user_class, "can_publish_articles"), (
                    "User should have business logic methods"
                )

        def test_api_layer(solution):
            """Test API layer implementation"""
            # Check for FastAPI app
            assert hasattr(solution, "app"), "FastAPI app should be defined"

            # Check for API endpoints (if using FastAPI)
            app = solution.app
            routes = [route.path for route in app.routes if hasattr(route, "path")]

            expected_routes = ["/api/auth", "/api/articles", "/api/comments"]
            for expected in expected_routes:
                assert any(expected in route for route in routes), (
                    f"Should have {expected} endpoint"
                )

        def test_clean_architecture(solution):
            """Test Clean Architecture principles"""
            # Domain should not depend on infrastructure
            if hasattr(solution, "User"):  # Domain entity
                user_source = inspect.getsource(solution.User)

                # Check for infrastructure dependencies
                infrastructure_imports = ["sqlalchemy", "fastapi", "requests"]
                for imp in infrastructure_imports:
                    assert imp.lower() not in user_source.lower(), (
                        f"Domain entity should not import {imp}"
                    )

        return [
            TestCase(
                "test_repository_pattern",
                "Repository pattern implementation",
                test_repository_pattern,
                "Architecture-Repository",
                3,
            ),
            TestCase(
                "test_service_layer",
                "Service layer implementation",
                test_service_layer,
                "Architecture-Service",
                3,
            ),
            TestCase(
                "test_domain_entities",
                "Domain entities implementation",
                test_domain_entities,
                "Architecture-Domain",
                4,
            ),
            TestCase(
                "test_api_layer",
                "API layer implementation",
                test_api_layer,
                "Architecture-API",
                3,
            ),
            TestCase(
                "test_clean_architecture",
                "Clean Architecture principles",
                test_clean_architecture,
                "Architecture-Clean",
                5,
            ),
        ]


class DDDTestSuite:
    """Test suite for Domain-Driven Design module"""

    @staticmethod
    def create_ddd_tests() -> List[TestCase]:
        """Create tests for DDD implementation"""

        def test_bounded_contexts(solution):
            """Test bounded contexts separation"""
            # Look for bounded context classes
            context_classes = [
                name
                for name in dir(solution)
                if any(ctx in name.lower() for ctx in ["customer", "product", "order"])
            ]
            assert len(context_classes) >= 6, (
                "Should have classes from different bounded contexts"
            )

        def test_value_objects(solution):
            """Test Value Objects implementation"""
            vo_classes = [
                name
                for name in dir(solution)
                if any(vo in name.lower() for vo in ["money", "email", "address"])
            ]
            assert len(vo_classes) >= 3, (
                "Should have Value Objects like Money, Email, Address"
            )

            # Test Money value object
            if hasattr(solution, "Money"):
                money_class = solution.Money
                # Test immutability and operations
                assert hasattr(money_class, "add"), "Money should have add method"
                assert hasattr(money_class, "multiply"), (
                    "Money should have multiply method"
                )

        def test_aggregates(solution):
            """Test Aggregate implementation"""
            # Look for aggregate classes
            aggregates = [
                name
                for name in dir(solution)
                if any(agg in name.lower() for agg in ["customer", "product", "order"])
                and not any(
                    skip in name.lower() for skip in ["id", "repository", "service"]
                )
            ]
            assert len(aggregates) >= 3, (
                "Should have Customer, Product, Order aggregates"
            )

            # Test aggregate roots have domain events
            for agg_name in aggregates:
                if hasattr(solution, agg_name):
                    agg_class = getattr(solution, agg_name)
                    methods = dir(agg_class)
                    assert any(
                        "domain_events" in method.lower()
                        or "get_events" in method.lower()
                        for method in methods
                    ), f"{agg_name} should manage domain events"

        def test_domain_events(solution):
            """Test Domain Events implementation"""
            event_classes = [
                name
                for name in dir(solution)
                if name.endswith("Event") or "Event" in name
            ]
            assert len(event_classes) >= 3, "Should have domain event classes"

            # Check for event base class
            if hasattr(solution, "DomainEvent"):
                event_base = solution.DomainEvent
                assert hasattr(event_base, "event_type"), (
                    "DomainEvent should have event_type method"
                )

        def test_repositories(solution):
            """Test Repository interfaces and implementations"""
            repo_classes = [name for name in dir(solution) if "Repository" in name]
            assert len(repo_classes) >= 4, (
                "Should have repository interfaces and implementations"
            )

            # Check for interface pattern
            interfaces = [name for name in repo_classes if name.startswith("I")]
            implementations = [
                name for name in repo_classes if not name.startswith("I")
            ]
            assert len(interfaces) >= 3, "Should have repository interfaces"
            assert len(implementations) >= 3, "Should have repository implementations"

        def test_ubiquitous_language(solution):
            """Test use of ubiquitous language in code"""
            # Check for domain-specific terminology
            domain_terms = ["CustomerId", "ProductId", "OrderId", "Money", "Email"]
            found_terms = [term for term in domain_terms if hasattr(solution, term)]
            assert len(found_terms) >= 4, (
                "Should use domain-specific types and terminology"
            )

        def test_business_rules(solution):
            """Test implementation of business rules"""
            # Look for business rule classes or validation logic
            rule_indicators = [
                name
                for name in dir(solution)
                if any(
                    indicator in name.lower()
                    for indicator in ["rule", "validate", "policy", "constraint"]
                )
            ]
            assert len(rule_indicators) >= 2, (
                "Should have business rules or validation logic"
            )

        return [
            TestCase(
                "test_bounded_contexts",
                "Bounded contexts separation",
                test_bounded_contexts,
                "DDD-Contexts",
                3,
            ),
            TestCase(
                "test_value_objects",
                "Value Objects implementation",
                test_value_objects,
                "DDD-ValueObjects",
                4,
            ),
            TestCase(
                "test_aggregates",
                "Aggregate design and implementation",
                test_aggregates,
                "DDD-Aggregates",
                5,
            ),
            TestCase(
                "test_domain_events",
                "Domain Events implementation",
                test_domain_events,
                "DDD-Events",
                4,
            ),
            TestCase(
                "test_repositories",
                "Repository pattern in DDD",
                test_repositories,
                "DDD-Repositories",
                3,
            ),
            TestCase(
                "test_ubiquitous_language",
                "Use of ubiquitous language",
                test_ubiquitous_language,
                "DDD-Language",
                3,
            ),
            TestCase(
                "test_business_rules",
                "Business rules implementation",
                test_business_rules,
                "DDD-Rules",
                4,
            ),
        ]


class ProjectTestSuite:
    """Test suite for complete project implementation"""

    @staticmethod
    def create_project_tests() -> List[TestCase]:
        """Create tests for complete project"""

        def test_solid_principles_applied(solution):
            """Test SOLID principles throughout the project"""
            # Check for dependency injection
            classes_with_init = []
            for name in dir(solution):
                obj = getattr(solution, name)
                if isinstance(obj, type) and hasattr(obj, "__init__"):
                    init_params = (
                        len(obj.__init__.__code__.co_varnames) - 1  # type: ignore[misc]
                    )  # -1 for self
                    if init_params > 2:  # Likely dependency injection
                        classes_with_init.append(name)

            assert len(classes_with_init) >= 3, (
                "Should use dependency injection (SOLID DIP)"
            )

        def test_design_patterns_integration(solution):
            """Test integration of multiple design patterns"""
            pattern_indicators = {
                "strategy": ["Strategy", "Payment"],
                "observer": ["Observer", "Event", "Notification"],
                "factory": ["Factory", "create"],
                "repository": ["Repository"],
                "command": ["Command"],
            }

            found_patterns = []
            for pattern, indicators in pattern_indicators.items():
                if any(
                    any(indicator.lower() in name.lower() for name in dir(solution))
                    for indicator in indicators
                ):
                    found_patterns.append(pattern)

            assert len(found_patterns) >= 4, (
                f"Should implement multiple patterns, found: {found_patterns}"
            )

        def test_clean_architecture_layers(solution):
            """Test proper architectural layering"""
            # Domain layer
            domain_classes = [
                name
                for name in dir(solution)
                if any(
                    domain in name
                    for domain in ["Customer", "Product", "Order", "Money", "Email"]
                )
            ]
            assert len(domain_classes) >= 5, "Should have rich domain layer"

            # Application layer
            app_services = [
                name
                for name in dir(solution)
                if "Service" in name and "Domain" not in name
            ]
            assert len(app_services) >= 1, "Should have application services"

            # Infrastructure layer
            infra_classes = [
                name
                for name in dir(solution)
                if any(infra in name for infra in ["Repository", "Model", "Store"])
            ]
            assert len(infra_classes) >= 3, "Should have infrastructure implementations"

        def test_async_implementation(solution):
            """Test async/await usage for scalability"""
            has_async = False

            # Try AST-based analysis if solution module has __file__ attribute
            if hasattr(solution, "__file__") and solution.__file__:
                try:
                    with open(solution.__file__, "r", encoding="utf-8") as f:
                        source_code = f.read()
                    tree = ast.parse(source_code)
                    # Check for async function definitions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.AsyncFunctionDef):
                            has_async = True
                            break
                except (OSError, SyntaxError, UnicodeDecodeError):
                    # Fallback to runtime checks if file reading fails
                    pass

            # Fallback to runtime checks using inspect.iscoroutinefunction
            if not has_async:
                for name in dir(solution):
                    if name.startswith("_"):
                        continue
                    try:
                        obj = getattr(solution, name)
                        if inspect.iscoroutinefunction(obj):
                            has_async = True
                            break
                    except (AttributeError, TypeError):
                        continue

            assert has_async, "Should implement async operations for scalability"

        def test_error_handling(solution):
            """Test proper error handling and domain exceptions"""
            error_classes = [
                name
                for name in dir(solution)
                if any(error in name for error in ["Error", "Exception"])
            ]
            assert len(error_classes) >= 1, (
                "Should have domain-specific exception classes"
            )

        def test_monitoring_and_observability(solution):
            """Test monitoring and observability features"""
            monitoring_indicators = [
                name
                for name in dir(solution)
                if any(
                    monitor in name.lower()
                    for monitor in ["metric", "logger", "log", "monitor"]
                )
            ]
            assert len(monitoring_indicators) >= 1, (
                "Should include monitoring/logging capabilities"
            )

        def test_api_endpoints(solution):
            """Test REST API implementation"""
            # Look for FastAPI or Flask indicators
            api_indicators = [
                name
                for name in dir(solution)
                if any(
                    api in name.lower() for api in ["app", "router", "endpoint", "api"]
                )
            ]
            assert len(api_indicators) >= 1, "Should have API implementation"

        def test_configuration_management(solution):
            """Test configuration and environment management"""
            config_indicators = [
                name
                for name in dir(solution)
                if any(
                    config in name.lower() for config in ["config", "setting", "env"]
                )
            ]
            assert len(config_indicators) >= 1, "Should have configuration management"

        def test_production_readiness(solution):
            """Test production-ready features"""
            prod_features = {
                "security": ["security", "auth", "jwt", "password", "hash"],
                "validation": ["validate", "pydantic", "schema"],
                "performance": ["cache", "background", "async"],
                "reliability": ["retry", "circuit", "health"],
            }

            found_features = []
            for feature, indicators in prod_features.items():
                if any(
                    any(indicator.lower() in name.lower() for name in dir(solution))
                    for indicator in indicators
                ):
                    found_features.append(feature)

            assert len(found_features) >= 2, (
                f"Should have production features: {found_features}"
            )

        return [
            TestCase(
                "test_solid_principles_applied",
                "SOLID principles throughout project",
                test_solid_principles_applied,
                "Project-SOLID",
                5,
            ),
            TestCase(
                "test_design_patterns_integration",
                "Multiple design patterns integration",
                test_design_patterns_integration,
                "Project-Patterns",
                5,
            ),
            TestCase(
                "test_clean_architecture_layers",
                "Clean architecture layering",
                test_clean_architecture_layers,
                "Project-Architecture",
                5,
            ),
            TestCase(
                "test_async_implementation",
                "Async/await implementation",
                test_async_implementation,
                "Project-Async",
                3,
            ),
            TestCase(
                "test_error_handling",
                "Error handling and domain exceptions",
                test_error_handling,
                "Project-Errors",
                3,
            ),
            TestCase(
                "test_monitoring_and_observability",
                "Monitoring and observability",
                test_monitoring_and_observability,
                "Project-Monitoring",
                4,
            ),
            TestCase(
                "test_api_endpoints",
                "REST API implementation",
                test_api_endpoints,
                "Project-API",
                4,
            ),
            TestCase(
                "test_configuration_management",
                "Configuration management",
                test_configuration_management,
                "Project-Config",
                3,
            ),
            TestCase(
                "test_production_readiness",
                "Production-ready features",
                test_production_readiness,
                "Project-Production",
                5,
            ),
        ]


# =============================================================================
# TEST EXECUTION ENGINE
# =============================================================================


class TestRunner:
    """Main test execution engine"""

    def __init__(self):
        self.results: List[TestExecutionResult] = []

    def run_test_case(
        self, test_case: TestCase, solution_module
    ) -> TestExecutionResult:
        """Run a single test case"""
        start_time = datetime.now()

        try:
            # Run the test
            test_case.test_function(solution_module)

            # Test passed
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestExecutionResult(
                test_case=test_case,
                result=TestResult.PASS,
                execution_time=execution_time,
                score=test_case.points,
            )

        except AssertionError as e:
            # Test failed
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestExecutionResult(
                test_case=test_case,
                result=TestResult.FAIL,
                execution_time=execution_time,
                error_message=str(e),
                score=0.0,
            )

        except Exception as e:
            # Test error
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestExecutionResult(
                test_case=test_case,
                result=TestResult.ERROR,
                execution_time=execution_time,
                error_message=f"{type(e).__name__}: {str(e)}",
                score=0.0,
            )

    def run_test_suite(
        self, test_suite: ModuleTestSuite, solution_file_path: str
    ) -> Dict[str, Any]:
        """Run complete test suite"""
        print(f"\n🧪 Running {test_suite.module_name} Test Suite")
        print("=" * 50)

        # Import solution
        solution = SolutionImporter.import_solution(solution_file_path)
        if solution is None:
            return {
                "module": test_suite.module_name,
                "status": "error",
                "error": "Failed to import solution",
                "results": [],
            }

        # Analyze code structure
        with open(solution_file_path, "r") as f:
            code_content = f.read()

        tree = CodeAnalyzer.parse_code(code_content)
        if tree:
            detected_patterns = CodeAnalyzer.find_design_patterns(tree)
            found_classes = CodeAnalyzer.find_classes(tree)
            print(f"📋 Detected classes: {', '.join(found_classes)}")
            print(
                f"🎨 Detected patterns: {[k for k, v in detected_patterns.items() if v]}"
            )

        # Run tests
        test_results = []
        total_score = 0.0

        for test_case in test_suite.test_cases:
            print(f"\n🔧 Running: {test_case.description}")

            result = self.run_test_case(test_case, solution)
            test_results.append(result)
            total_score += result.score

            if result.result == TestResult.PASS:
                print(f"✅ PASS ({result.score}/{test_case.points} points)")
            elif result.result == TestResult.FAIL:
                print(f"❌ FAIL: {result.error_message}")
            else:
                print(f"💥 ERROR: {result.error_message}")

        # Calculate final score
        percentage = (
            (total_score / test_suite.max_points) * 100
            if test_suite.max_points > 0
            else 0
        )

        print("\n📊 Test Suite Results:")
        print(f"Score: {total_score}/{test_suite.max_points} ({percentage:.1f}%)")

        return {
            "module": test_suite.module_name,
            "status": "completed",
            "total_score": total_score,
            "max_score": test_suite.max_points,
            "percentage": percentage,
            "results": test_results,
            "detected_patterns": detected_patterns if tree else {},
            "found_classes": found_classes if tree else [],
        }


# =============================================================================
# MAIN TESTING INTERFACE
# =============================================================================


class AutomatedTester:
    """
    Main interface for automated testing.

    💡 Простыми словами: Это главный "проверяющий" - он запускает все тесты
    для вашего кода и выдает подробный отчет. Как автоматический экзаменатор.

    Features:
    - Runs multiple test suites
    - Analyzes code structure
    - Detects design patterns
    - Provides detailed feedback

    Example:
        >>> tester = AutomatedTester()
        >>> result = tester.test_solution("my_solution.py", "solid-srp")
        >>> print(f"Score: {result['total_score']}/{result['max_score']}")
    """

    def __init__(self):
        """
        Initialize the automated tester.

        💡 Простыми словами: Создает тестера и загружает все наборы тестов.
        """
        self.test_runner = TestRunner()
        self.test_suites = self._initialize_test_suites()

    def _initialize_test_suites(self) -> Dict[str, ModuleTestSuite]:
        """Initialize all test suites"""
        return {
            "solid-srp": ModuleTestSuite(
                "SOLID - Single Responsibility Principle",
                SOLIDTestSuite.create_srp_tests(),
            ),
            "patterns-ecommerce": ModuleTestSuite(
                "Design Patterns - E-commerce System",
                DesignPatternsTestSuite.create_pattern_tests(),
            ),
            "architecture-blog": ModuleTestSuite(
                "Architecture - Blog Platform",
                ArchitectureTestSuite.create_architecture_tests(),
            ),
            "ddd-ecommerce": ModuleTestSuite(
                "Domain-Driven Design - E-commerce Domain",
                DDDTestSuite.create_ddd_tests(),
            ),
            "project-implementation": ModuleTestSuite(
                "Complete Project Implementation",
                ProjectTestSuite.create_project_tests(),
            ),
        }

    def test_solution(
        self, solution_file: str, test_suite_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test a solution file against test suites.

        💡 Простыми словами: Проверяет ваш файл с решением. Может проверить
        против конкретного набора тестов или всех подходящих.

        Args:
            solution_file: Путь к файлу с вашим решением
            test_suite_name: Имя набора тестов (опционально). Если не указано,
                           запускаются все подходящие тесты.

                           Доступные наборы:
                           - 'solid-srp': Тесты для SOLID принципов
                           - 'patterns-ecommerce': Тесты для паттернов
                           - 'architecture-blog': Тесты для архитектуры
                           - 'ddd-ecommerce': Тесты для DDD
                           - 'project-implementation': Тесты для проекта

        Returns:
            Dict с результатами тестирования:
            {
                'module': название модуля,
                'status': 'completed' или 'error',
                'total_score': набранные баллы,
                'max_score': максимальные баллы,
                'percentage': процент выполнения,
                'results': детальные результаты каждого теста,
                'detected_patterns': найденные паттерны,
                'found_classes': найденные классы
            }

        Example:
            >>> tester = AutomatedTester()
            >>> # Проверить только SOLID тесты
            >>> result = tester.test_solution("solution.py", "solid-srp")
            >>> print(f"Score: {result['total_score']}/{result['max_score']}")

            >>> # Проверить все подходящие тесты
            >>> results = tester.test_solution("solution.py")
            >>> for suite_name, result in results.items():
            ...     print(f"{suite_name}: {result['percentage']:.1f}%")

        Errors:
            Если файл не найден, возвращает {'error': 'сообщение об ошибке'}
        """
        if not os.path.exists(solution_file):
            error_msg = f"Solution file not found: {solution_file}"
            print(f"❌ {error_msg}")
            print("💡 Tip: Make sure the file path is correct.")
            print(f"   Current directory: {os.getcwd()}")
            return {"error": error_msg}

        results = {}

        if test_suite_name:
            # Run specific test suite
            if test_suite_name in self.test_suites:
                suite = self.test_suites[test_suite_name]
                results[test_suite_name] = self.test_runner.run_test_suite(
                    suite, solution_file
                )
            else:
                return {"error": f"Test suite not found: {test_suite_name}"}
        else:
            # Run all applicable test suites
            for suite_name, suite in self.test_suites.items():
                try:
                    results[suite_name] = self.test_runner.run_test_suite(
                        suite, solution_file
                    )
                except Exception as e:
                    results[suite_name] = {"status": "error", "error": str(e)}

        return results

    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate detailed test report"""
        report = []
        report.append("📋 AUTOMATED TESTING REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        total_score = 0
        total_max_score = 0

        for suite_name, results in test_results.items():
            if "error" in results:
                report.append(f"❌ {suite_name}: {results['error']}")
                continue

            report.append(f"📚 {results['module']}")
            report.append("-" * 30)
            report.append(
                f"Score: {results['total_score']}/{results['max_score']} ({results['percentage']:.1f}%)"
            )

            total_score += results["total_score"]
            total_max_score += results["max_score"]

            if "detected_patterns" in results:
                patterns = [k for k, v in results["detected_patterns"].items() if v]
                if patterns:
                    report.append(f"🎨 Detected Patterns: {', '.join(patterns)}")

            if "found_classes" in results:
                classes = results["found_classes"][:5]  # Show first 5 classes
                if classes:
                    report.append(f"📋 Found Classes: {', '.join(classes)}")

            # Individual test results
            for test_result in results["results"]:
                status_icon = "✅" if test_result.result == TestResult.PASS else "❌"
                report.append(f"  {status_icon} {test_result.test_case.description}")
                if test_result.error_message:
                    report.append(f"     Error: {test_result.error_message}")

            report.append("")

        # Overall summary
        overall_percentage = (
            (total_score / total_max_score) * 100 if total_max_score > 0 else 0
        )
        report.append("🏆 OVERALL SUMMARY")
        report.append("-" * 20)
        report.append(
            f"Total Score: {total_score}/{total_max_score} ({overall_percentage:.1f}%)"
        )

        if overall_percentage >= 90:
            report.append("🎉 Excellent work!")
        elif overall_percentage >= 75:
            report.append("👍 Good job!")
        elif overall_percentage >= 60:
            report.append("📈 Keep improving!")
        else:
            report.append("💪 More practice needed!")

        return "\n".join(report)


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================


def main():
    """
    Main CLI interface for the automated testing system.

    💡 Простыми словами: Командная строка для запуска тестов.
    Вы указываете файл с решением, и система проверяет его.

    Usage Examples:
        # Проверить решение против всех тестов
        python test_runner.py my_solution.py

        # Проверить только SOLID тесты
        python test_runner.py my_solution.py --suite solid-srp

        # Создать подробный отчет
        python test_runner.py my_solution.py --report

        # Запустить демо
        python test_runner.py --demo

    Arguments:
        solution_file: Путь к файлу с вашим решением
        --suite NAME: Запустить только указанный набор тестов
        --report: Создать подробный текстовый отчет
        --demo: Показать демонстрацию системы

    Available Test Suites:
        - solid-srp: SOLID принципы (Single Responsibility)
        - patterns-ecommerce: Паттерны проектирования
        - architecture-blog: Архитектурные паттерны
        - ddd-ecommerce: Domain-Driven Design
        - project-implementation: Полная реализация проекта

    Output:
        Система выводит:
        - ✅ Успешные тесты
        - ❌ Неудачные тесты с объяснениями
        - 📊 Общий балл и процент
        - 🎨 Найденные паттерны
        - 💾 Отчет (если указан --report)
    """
    import argparse

    # Initialize tester early to get available test suites dynamically
    tester = AutomatedTester()
    available_suites = list(tester.test_suites.keys())

    parser = argparse.ArgumentParser(
        description="Automated Testing System for Student Solutions"
    )
    parser.add_argument("solution_file", help="Path to student solution file")
    parser.add_argument(
        "--suite", help="Specific test suite to run", choices=available_suites
    )
    parser.add_argument(
        "--report", help="Generate detailed report", action="store_true"
    )

    args = parser.parse_args()

    print("🤖 Automated Testing System")
    print("=" * 50)
    print(f"Testing solution: {args.solution_file}")

    if args.suite:
        print(f"Test suite: {args.suite}")
    else:
        print("Running all applicable test suites...")

    # Run tests
    results = tester.test_solution(args.solution_file, args.suite)

    # Generate and display report
    if args.report:
        report = tester.generate_report(results)
        print("\n" + report)

        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\n💾 Report saved to: {report_file}")
    else:
        # Simple summary
        for suite_name, result in results.items():
            if "error" in result:
                print(f"❌ {suite_name}: {result['error']}")
            else:
                print(
                    f"✅ {result['module']}: {result['total_score']}/{result['max_score']} ({result['percentage']:.1f}%)"
                )


def demo_testing():
    """Demonstrate the testing system"""
    print("🧪 Automated Testing System Demo")
    print("=" * 50)

    tester = AutomatedTester()

    print("📋 Available Test Suites:")
    for suite_name, suite in tester.test_suites.items():
        print(
            f"  • {suite_name}: {suite.module_name} ({len(suite.test_cases)} tests, {suite.max_points} points)"
        )

    print("\n🎯 Test Categories:")
    print("  • Code Structure Analysis")
    print("  • Design Pattern Detection")
    print("  • Architecture Compliance")
    print("  • Functional Testing")
    print("  • Best Practices Validation")

    print("\n🚀 Usage Examples:")
    print("  python test_runner.py solution.py --suite solid-srp")
    print("  python test_runner.py solution.py --report")
    print("  python test_runner.py solution.py")  # Run all tests

    print("\n✨ Features:")
    print("  • Automatic pattern recognition")
    print("  • Code quality analysis")
    print("  • Detailed error reporting")
    print("  • Scoring system")
    print("  • Progress tracking")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo_testing()
    else:
        main()
