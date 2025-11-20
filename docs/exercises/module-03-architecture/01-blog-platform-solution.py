#!/usr/bin/env python3
"""
Solution for Blog Platform Monolithic Architecture
Module 03: Architecture - Complete Implementation

This solution demonstrates a well-structured monolithic architecture
for a blog platform using Python, FastAPI, SQLAlchemy, and following
clean architecture principles.

Architecture Layers:
- Domain Layer (entities, value objects, domain services)
- Application Layer (use cases, services)
- Infrastructure Layer (repositories, external services)
- Presentation Layer (API controllers, schemas)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from enum import Enum
import uuid
from dataclasses import dataclass, field
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
from contextlib import contextmanager
import logging
import os
import bleach  # type: ignore[import-untyped]
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import urllib.request
import urllib.error
import urllib.parse
import socket

# Optional dependency for password strength checking
try:
    import zxcvbn  # type: ignore[import-untyped]

    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False

# Configuration constants
# HaveIBeenPwned API timeout (in seconds)
# Can be overridden via HIBP_API_TIMEOUT environment variable
try:
    timeout_value = os.getenv("HIBP_API_TIMEOUT", "8.0")
    HIBP_API_TIMEOUT = float(timeout_value)
except (ValueError, TypeError) as e:
    logging.warning(
        f"Invalid HIBP_API_TIMEOUT value '{timeout_value}': {e}. "
        f"Using default value 8.0 seconds."
    )
    HIBP_API_TIMEOUT = 8.0


# =============================================================================
# DOMAIN LAYER - Core Business Logic
# =============================================================================


class ArticleStatus(Enum):
    """Article status enumeration"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserRole(Enum):
    """User role enumeration"""

    READER = "reader"
    AUTHOR = "author"
    EDITOR = "editor"
    ADMIN = "admin"


# Domain Entities
@dataclass
class User:
    """
    User domain entity.

    💡 Простыми словами: Это основная сущность пользователя в системе.
    Содержит информацию о пользователе и бизнес-логику проверки прав доступа.

    Clean Architecture - Domain Layer:
    - ✅ Содержит бизнес-логику (can_publish_articles, can_edit_article)
    - ✅ Не зависит от инфраструктуры (БД, API)
    - ✅ Является частью доменного слоя

    Example:
        >>> user = User(
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     role=UserRole.AUTHOR
        ... )
        >>> print(user.can_publish_articles())
        True
    """

    id: Optional[str] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.READER
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def can_publish_articles(self) -> bool:
        """Check if user can publish articles"""
        return self.role in [UserRole.AUTHOR, UserRole.EDITOR, UserRole.ADMIN]

    def can_edit_article(self, article_author_id: str) -> bool:
        """Check if user can edit a specific article"""
        return self.id == article_author_id or self.role in [
            UserRole.EDITOR,
            UserRole.ADMIN,
        ]

    def can_delete_article(self, article_author_id: str) -> bool:
        """Check if user can delete a specific article"""
        return self.id == article_author_id or self.role == UserRole.ADMIN


@dataclass
class Article:
    """Article domain entity"""

    id: Optional[str] = None
    title: str = ""
    content: str = ""
    excerpt: str = ""
    slug: str = ""
    status: ArticleStatus = ArticleStatus.DRAFT
    author_id: str = ""
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.excerpt and self.content:
            # Generate excerpt from content (first 150 chars)
            self.excerpt = (
                self.content[:150] + "..." if len(self.content) > 150 else self.content
            )
        if not self.slug and self.title:
            # Generate slug from title
            self.slug = Article._generate_slug(self.title)

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re

        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[\s_-]+", "-", slug)
        return slug.strip("-")

    def publish(self):
        """Publish the article"""
        if self.status == ArticleStatus.DRAFT:
            self.status = ArticleStatus.PUBLISHED
            self.published_at = datetime.now(timezone.utc)

    def archive(self):
        """Archive the article"""
        self.status = ArticleStatus.ARCHIVED

    def is_published(self) -> bool:
        """Check if article is published"""
        return self.status == ArticleStatus.PUBLISHED

    def word_count(self) -> int:
        """Calculate word count"""
        return len(self.content.split()) if self.content else 0


@dataclass
class Comment:
    """Comment domain entity"""

    id: Optional[str] = None
    content: str = ""
    article_id: str = ""
    author_id: str = ""
    parent_id: Optional[str] = None  # For reply functionality
    is_approved: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def approve(self):
        """Approve the comment"""
        self.is_approved = True

    def is_reply(self) -> bool:
        """Check if comment is a reply"""
        return self.parent_id is not None


# Domain Services
class SlugService:
    """Domain service for slug generation and validation"""

    @staticmethod
    def generate_unique_slug(title: str, existing_slugs: List[str]) -> str:
        """Generate unique slug"""
        base_slug = Article._generate_slug(title)

        if base_slug not in existing_slugs:
            return base_slug

        # Add number suffix if slug exists
        counter = 1
        while f"{base_slug}-{counter}" in existing_slugs:
            counter += 1

        return f"{base_slug}-{counter}"


class AuthenticationService:
    """Domain service for authentication logic"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def generate_jwt_token(
        user_id: str, secret_key: str, expires_in_hours: int = 24
    ) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")  # type: ignore[attr-defined]

    @staticmethod
    def verify_jwt_token(token: str, secret_key: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])  # type: ignore[attr-defined]
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:  # type: ignore[attr-defined]
            return None
        except jwt.InvalidTokenError:  # type: ignore[attr-defined]
            return None


# =============================================================================
# INFRASTRUCTURE LAYER - Data Access and External Services
# =============================================================================

# Database Configuration
DATABASE_URL = "sqlite:///./blog_platform.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Models (ORM)
Base = declarative_base()  # type: ignore[misc,valid-type]

# Association table for article tags
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", String, ForeignKey("articles.id")),
    Column("tag_name", String, ForeignKey("tags.name")),
)

class UserModel(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String, default=UserRole.READER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    articles = relationship("ArticleModel", back_populates="author")
    comments = relationship("CommentModel", back_populates="author")


class ArticleModel(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "articles"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    excerpt = Column(Text)
    slug = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default=ArticleStatus.DRAFT.value)
    author_id = Column(String, ForeignKey("users.id"))
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    author = relationship("UserModel", back_populates="articles")
    comments = relationship("CommentModel", back_populates="article")
    tags = relationship("TagModel", secondary=article_tags, back_populates="articles")


class CommentModel(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    article_id = Column(String, ForeignKey("articles.id"))
    author_id = Column(String, ForeignKey("users.id"))
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    article = relationship("ArticleModel", back_populates="comments")
    author = relationship("UserModel", back_populates="comments")
    replies = relationship("CommentModel", remote_side="CommentModel.parent_id")


class TagModel(Base):  # type: ignore[misc,valid-type]
    __tablename__ = "tags"

    name = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    articles = relationship(
        "ArticleModel", secondary=article_tags, back_populates="tags"
    )


# Repository Interfaces
class IUserRepository(ABC):
    """
    Repository interface for user persistence.

    💡 Простыми словами: Это интерфейс для работы с пользователями в БД.
    Repository Pattern скрывает детали работы с базой данных и позволяет
    легко менять способ хранения (SQL, NoSQL, файлы) без изменения бизнес-логики.

    Repository Pattern:
    - ✅ Абстракция над хранилищем данных
    - ✅ Инкапсулирует логику доступа к данным
    - ✅ Упрощает тестирование (можно использовать mock-репозиторий)

    Clean Architecture - Infrastructure Layer:
    - ✅ Реализация находится в Infrastructure Layer
    - ✅ Domain Layer зависит только от интерфейса

    Example:
        >>> repository = SQLUserRepository(session)
        >>> user = User(username="john", email="john@example.com")
        >>> saved_user = repository.save(user)
        >>> print(saved_user.id)
        'uuid-...'
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save user to repository.

        💡 Простыми словами: Сохраняет пользователя в хранилище.

        Args:
            user: Пользователь для сохранения

        Returns:
            User: Сохраненный пользователь с присвоенным ID
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        pass


class IArticleRepository(ABC):
    @abstractmethod
    def save(self, article: Article) -> Article:
        pass

    @abstractmethod
    def find_by_id(self, article_id: str) -> Optional[Article]:
        pass

    @abstractmethod
    def find_by_slug(self, slug: str) -> Optional[Article]:
        pass

    @abstractmethod
    def get_existing_slugs(self) -> List[str]:
        pass

    @abstractmethod
    def find_by_author(
        self, author_id: str, page: int = 1, per_page: int = 20
    ) -> List[Article]:
        pass

    @abstractmethod
    def find_published(self, page: int = 1, per_page: int = 20) -> List[Article]:
        pass

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> List[Article]:
        pass

    @abstractmethod
    def delete(self, article_id: str) -> bool:
        pass


class ICommentRepository(ABC):
    @abstractmethod
    def save(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    def find_by_article(self, article_id: str) -> List[Comment]:
        pass

    @abstractmethod
    def find_by_id(self, comment_id: str) -> Optional[Comment]:
        pass

    @abstractmethod
    def delete(self, comment_id: str) -> bool:
        pass


# Repository Implementations
class SQLUserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:
        user_model = self._to_model(user)
        existing = self.session.query(UserModel).filter(UserModel.id == user.id).first()

        if existing:
            # Update existing
            for key, value in user_model.__dict__.items():
                if key != "_sa_instance_state":
                    setattr(existing, key, value)
            self.session.commit()
            return self._to_entity(existing)
        else:
            # Create new
            self.session.add(user_model)
            self.session.commit()
            return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_username(self, username: str) -> Optional[User]:
        model = (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def find_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        offset = (page - 1) * per_page
        models = self.session.query(UserModel).offset(offset).limit(per_page).all()
        return [self._to_entity(model) for model in models]

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _to_entity(self, model: UserModel) -> User:
        # SQLAlchemy Column types are compatible at runtime with domain types
        return User(  # type: ignore
            id=model.id,  # type: ignore[arg-type]
            username=model.username,  # type: ignore[arg-type]
            email=model.email,  # type: ignore[arg-type]
            password_hash=model.password_hash,  # type: ignore[arg-type]
            first_name=model.first_name,  # type: ignore[arg-type]
            last_name=model.last_name,  # type: ignore[arg-type]
            role=UserRole(model.role),
            is_active=model.is_active,  # type: ignore[arg-type]
            created_at=model.created_at,  # type: ignore[arg-type]
            updated_at=model.updated_at,  # type: ignore[arg-type]
        )


class SQLArticleRepository(IArticleRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, article: Article) -> Article:
        article_model = self._to_model(article)
        existing = (
            self.session.query(ArticleModel)
            .filter(ArticleModel.id == article.id)
            .first()
        )

        if existing:
            # Update existing
            for key, value in article_model.__dict__.items():
                if key not in ["_sa_instance_state", "tags"]:
                    setattr(existing, key, value)
            self.session.commit()
            return article
        else:
            # Create new
            self.session.add(article_model)
            self.session.commit()
            return article

    def find_by_id(self, article_id: str) -> Optional[Article]:
        model = (
            self.session.query(ArticleModel)
            .filter(ArticleModel.id == article_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_slug(self, slug: str) -> Optional[Article]:
        model = (
            self.session.query(ArticleModel).filter(ArticleModel.slug == slug).first()
        )
        return self._to_entity(model) if model else None

    def find_by_author(
        self, author_id: str, page: int = 1, per_page: int = 20
    ) -> List[Article]:
        offset = (page - 1) * per_page
        models = (
            self.session.query(ArticleModel)
            .filter(ArticleModel.author_id == author_id)
            .offset(offset)
            .limit(per_page)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def find_published(self, page: int = 1, per_page: int = 20) -> List[Article]:
        offset = (page - 1) * per_page
        models = (
            self.session.query(ArticleModel)
            .filter(ArticleModel.status == ArticleStatus.PUBLISHED.value)
            .order_by(ArticleModel.published_at.desc())
            .offset(offset)
            .limit(per_page)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def search(self, query: str, page: int = 1, per_page: int = 20) -> List[Article]:
        offset = (page - 1) * per_page
        models = (
            self.session.query(ArticleModel)
            .filter(
                (ArticleModel.title.contains(query))
                | (ArticleModel.content.contains(query))
            )
            .filter(ArticleModel.status == ArticleStatus.PUBLISHED.value)
            .offset(offset)
            .limit(per_page)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def delete(self, article_id: str) -> bool:
        model = (
            self.session.query(ArticleModel)
            .filter(ArticleModel.id == article_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def get_existing_slugs(self) -> List[str]:
        """Get all existing slugs"""
        return [slug[0] for slug in self.session.query(ArticleModel.slug).all()]

    def _to_model(self, article: Article) -> ArticleModel:
        return ArticleModel(
            id=article.id,
            title=article.title,
            content=article.content,
            excerpt=article.excerpt,
            slug=article.slug,
            status=article.status.value,
            author_id=article.author_id,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    def _to_entity(self, model: ArticleModel) -> Article:
        # SQLAlchemy Column types are compatible at runtime with domain types
        return Article(  # type: ignore
            id=model.id,  # type: ignore[arg-type]
            title=model.title,  # type: ignore[arg-type]
            content=model.content,  # type: ignore[arg-type]
            excerpt=model.excerpt,  # type: ignore[arg-type]
            slug=model.slug,  # type: ignore[arg-type]
            status=ArticleStatus(model.status),
            author_id=model.author_id,  # type: ignore[arg-type]
            published_at=model.published_at,  # type: ignore[arg-type]
            created_at=model.created_at,  # type: ignore[arg-type]
            updated_at=model.updated_at,  # type: ignore[arg-type]
            tags=[tag.name for tag in model.tags] if model.tags else [],
        )


class SQLCommentRepository(ICommentRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, comment: Comment) -> Comment:
        comment_model = self._to_model(comment)
        existing = (
            self.session.query(CommentModel)
            .filter(CommentModel.id == comment.id)
            .first()
        )

        if existing:
            # Update existing
            for key, value in comment_model.__dict__.items():
                if key != "_sa_instance_state":
                    setattr(existing, key, value)
            self.session.commit()
            return comment
        else:
            # Create new
            self.session.add(comment_model)
            self.session.commit()
            return comment

    def find_by_article(self, article_id: str) -> List[Comment]:
        models = (
            self.session.query(CommentModel)
            .filter(CommentModel.article_id == article_id)
            .filter(CommentModel.is_approved)
            .order_by(CommentModel.created_at.desc())
            .all()
        )
        return [self._to_entity(model) for model in models]

    def find_by_id(self, comment_id: str) -> Optional[Comment]:
        model = (
            self.session.query(CommentModel)
            .filter(CommentModel.id == comment_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def delete(self, comment_id: str) -> bool:
        model = (
            self.session.query(CommentModel)
            .filter(CommentModel.id == comment_id)
            .first()
        )
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def _to_model(self, comment: Comment) -> CommentModel:
        return CommentModel(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            author_id=comment.author_id,
            parent_id=comment.parent_id,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
        )

    def _to_entity(self, model: CommentModel) -> Comment:
        # SQLAlchemy Column types are compatible at runtime with domain types
        return Comment(  # type: ignore
            id=model.id,  # type: ignore[arg-type]
            content=model.content,  # type: ignore[arg-type]
            article_id=model.article_id,  # type: ignore[arg-type]
            author_id=model.author_id,  # type: ignore[arg-type]
            parent_id=model.parent_id,  # type: ignore[arg-type]
            is_approved=model.is_approved,  # type: ignore[arg-type]
            created_at=model.created_at,  # type: ignore[arg-type]
        )


# =============================================================================
# APPLICATION LAYER - Use Cases and Services
# =============================================================================


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


def validate_password_strength(
    password: str, api_timeout: Optional[float] = None
) -> None:
    """
    Validate password strength with multiple checks:
    1. Minimum length (12 characters)
    2. Password strength using zxcvbn (score >= 3)
    3. Compromised password check via HaveIBeenPwned API

    Args:
        password: Password to validate
        api_timeout: Optional timeout for HaveIBeenPwned API request in seconds.
                     If not provided, uses HIBP_API_TIMEOUT constant or env var.

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    # Check minimum length first
    if len(password) < 12:
        raise ValidationError("Password must be at least 12 characters long")

    # Check password strength using zxcvbn if available
    if ZXCVBN_AVAILABLE:
        try:
            result = zxcvbn.zxcvbn(password)
            score = result.get("score", 0) if isinstance(result, dict) else 0
            if score < 3:
                error_msg = "Password is too weak. "

                # Extract feedback if available
                feedback = result.get("feedback") if isinstance(result, dict) else None
                if feedback and isinstance(feedback, dict):
                    warning = feedback.get("warning", "")
                    suggestions = feedback.get("suggestions", [])

                    if warning:
                        error_msg += f"{warning} "
                    if suggestions and isinstance(suggestions, list):
                        error_msg += "Suggestions: " + "; ".join(suggestions[:2])
                    else:
                        error_msg += "Please use a stronger password with a mix of uppercase, lowercase, numbers, and symbols."
                else:
                    error_msg += "Please use a stronger password with a mix of uppercase, lowercase, numbers, and symbols."

                raise ValidationError(error_msg)
        except ValidationError:
            # Re-raise ValidationError from zxcvbn check
            raise
        except Exception as e:
            # If zxcvbn fails, log but continue with other checks
            logging.warning(f"Password strength check failed: {e}")

    # Check if password is compromised via HaveIBeenPwned API
    try:
        # Use k-anonymity: only send first 5 chars of SHA-1 hash
        password_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = password_hash[:5]
        suffix = password_hash[5:]

        # Query HaveIBeenPwned API
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={"User-Agent": "BlogPlatform/1.0"})

        # Use provided timeout or fall back to configured constant
        timeout = api_timeout if api_timeout is not None else HIBP_API_TIMEOUT

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_text = response.read().decode("utf-8")

                # Check if our password suffix appears in the response
                for line in response_text.splitlines():
                    hash_suffix, count = line.split(":", 1)
                    if hash_suffix == suffix:
                        raise ValidationError(
                            f"This password has been found in {count} data breaches. "
                            "Please choose a different password."
                        )
        except urllib.error.URLError as e:
            # Network error or timeout - check if it's a timeout
            if isinstance(e.reason, socket.timeout):
                logging.warning(
                    f"HaveIBeenPwned API check timed out: {e}. Continuing with other validations."
                )
            else:
                logging.warning(
                    f"HaveIBeenPwned API check failed: {e}. Continuing with other validations."
                )
        except urllib.error.HTTPError as e:
            # HTTP error - fallback gracefully
            logging.warning(
                f"HaveIBeenPwned API returned error {e.code}: {e.reason}. Continuing with other validations."
            )
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # Encoding/decoding errors - log with traceback and continue
            logging.exception(
                f"Password compromise check failed due to encoding error: {e}. Continuing with other validations."
            )
        except ValueError as e:
            # Value parsing errors (e.g., from split operations) - log with traceback and continue
            logging.exception(
                f"Password compromise check failed due to parsing error: {e}. Continuing with other validations."
            )
    except Exception as e:
        # Unexpected errors - log with traceback and re-raise to avoid hiding bugs
        logging.exception(f"Unexpected error in password compromise check: {e}")
        raise


class UserService:
    """Application service for user operations"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """Register new user"""
        # Validate input
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")

        # Validate password strength (length, strength, compromised check)
        validate_password_strength(password)

        # Check for existing user
        if self.user_repository.find_by_username(username):
            raise ValidationError("Username already exists")
        if self.user_repository.find_by_email(email):
            raise ValidationError("Email already exists")

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=AuthenticationService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
        )

        return self.user_repository.save(user)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.user_repository.find_by_username(username)
        if user and AuthenticationService.verify_password(password, user.password_hash):
            return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.find_by_id(user_id)


class ArticleService:
    """Application service for article operations"""

    def __init__(
        self, article_repository: IArticleRepository, user_repository: IUserRepository
    ):
        self.article_repository = article_repository
        self.user_repository = user_repository
        self.logger = logging.getLogger(__name__)

    def create_article(
        self, title: str, content: str, author_id: str, tags: Optional[List[str]] = None
    ) -> Article:
        """Create new article"""
        # Validate author exists and can publish
        author = self.user_repository.find_by_id(author_id)
        if not author:
            raise ValidationError("Author not found")
        if not author.can_publish_articles():
            raise AuthorizationError("User cannot publish articles")

        # Generate unique slug
        existing_slugs = self.article_repository.get_existing_slugs()
        slug = SlugService.generate_unique_slug(title, existing_slugs)

        # Create article
        article = Article(
            title=title,
            content=content,
            author_id=author_id,
            slug=slug,
            tags=tags or [],
        )

        return self.article_repository.save(article)

    def publish_article(self, article_id: str, user_id: str) -> Article:
        """Publish article"""
        article = self.article_repository.find_by_id(article_id)
        if not article:
            raise ValidationError("Article not found")

        user = self.user_repository.find_by_id(user_id)
        if not user or not user.can_edit_article(article.author_id):
            raise AuthorizationError("Cannot publish this article")

        article.publish()
        return self.article_repository.save(article)

    def update_article(
        self,
        article_id: str,
        user_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Article:
        """Update article"""
        article = self.article_repository.find_by_id(article_id)
        if not article:
            raise ValidationError("Article not found")

        user = self.user_repository.find_by_id(user_id)
        if not user or not user.can_edit_article(article.author_id):
            raise AuthorizationError("Cannot edit this article")

        # Update fields
        if title:
            article.title = title
            # Regenerate slug if title changed
            existing_slugs = self.article_repository.get_existing_slugs()
            if article.slug in existing_slugs:
                existing_slugs.remove(article.slug)  # Remove current slug
            else:
                # Log warning if slug not found - potential data integrity issue
                self.logger.warning(
                    f"Article slug '{article.slug}' (ID: {article_id}) not found in existing slugs "
                    f"during update. This may indicate a data integrity problem."
                )
            article.slug = SlugService.generate_unique_slug(title, existing_slugs)

        if content:
            article.content = content
            # Regenerate excerpt
            article.excerpt = content[:150] + "..." if len(content) > 150 else content

        if tags is not None:
            article.tags = tags

        article.updated_at = datetime.now(timezone.utc)
        return self.article_repository.save(article)

    def delete_article(self, article_id: str, user_id: str) -> bool:
        """Delete article"""
        article = self.article_repository.find_by_id(article_id)
        if not article:
            raise ValidationError("Article not found")

        user = self.user_repository.find_by_id(user_id)
        if not user or not user.can_delete_article(article.author_id):
            raise AuthorizationError("Cannot delete this article")

        return self.article_repository.delete(article_id)

    def get_published_articles(
        self, page: int = 1, per_page: int = 20
    ) -> List[Article]:
        """Get published articles"""
        return self.article_repository.find_published(page, per_page)

    def search_articles(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> List[Article]:
        """Search articles"""
        return self.article_repository.search(query, page, per_page)

    def get_article_by_slug(self, slug: str) -> Optional[Article]:
        """Get article by slug"""
        return self.article_repository.find_by_slug(slug)


class CommentService:
    """Application service for comment operations"""

    def __init__(
        self,
        comment_repository: ICommentRepository,
        article_repository: IArticleRepository,
        user_repository: IUserRepository,
    ):
        self.comment_repository = comment_repository
        self.article_repository = article_repository
        self.user_repository = user_repository

    def add_comment(
        self, article_id: str, content: str, author_id: str, parent_id: Optional[str] = None
    ) -> Comment:
        """Add comment to article"""
        # Validate article exists and is published
        article = self.article_repository.find_by_id(article_id)
        if not article or not article.is_published():
            raise ValidationError("Article not found or not published")

        # Validate author exists
        author = self.user_repository.find_by_id(author_id)
        if not author:
            raise ValidationError("Author not found")

        # Validate parent comment exists if this is a reply
        if parent_id:
            parent = self.comment_repository.find_by_id(parent_id)
            if not parent or parent.article_id != article_id:
                raise ValidationError("Parent comment not found")

        # Create comment
        comment = Comment(
            content=content,
            article_id=article_id,
            author_id=author_id,
            parent_id=parent_id,
            is_approved=True,  # Auto-approve for now
        )

        return self.comment_repository.save(comment)

    def get_article_comments(self, article_id: str) -> List[Comment]:
        """Get approved comments for article"""
        return self.comment_repository.find_by_article(article_id)


# =============================================================================
# PRESENTATION LAYER - API Controllers and Schemas
# =============================================================================


# Pydantic Schemas for API
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    excerpt: str
    slug: str
    status: str
    author_id: str
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    word_count: int


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None


class CommentResponse(BaseModel):
    id: str
    content: str
    article_id: str
    author_id: str
    parent_id: Optional[str]
    created_at: datetime


# =============================================================================
# Security Utilities - XSS Protection
# =============================================================================

# Allowed tags and attributes for article content
# Using strict allowlist approach: only safe HTML tags and attributes are permitted
ALLOWED_TAGS = [
    "a",
    "p",
    "br",
    "strong",
    "em",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "pre",
    "code",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "p": [],
    "br": [],
    "strong": [],
    "em": [],
    "u": [],
    "h1": [],
    "h2": [],
    "h3": [],
    "h4": [],
    "h5": [],
    "h6": [],
    "ul": [],
    "ol": [],
    "li": [],
    "blockquote": [],
    "pre": [],
    "code": ["class"],
}


def sanitize_title(title: str) -> str:
    """
    Sanitize article title by stripping all HTML tags.
    Title should be plain text only to prevent XSS attacks.

    Args:
        title: Raw title string that may contain HTML

    Returns:
        Plain text title with all HTML tags removed
    """
    # Strip all HTML tags - title must be plain text
    return bleach.clean(title, tags=[], strip=True)


def sanitize_content(content: str) -> str:
    """
    Sanitize article content using strict allowlist approach.
    Only safe HTML tags and attributes are permitted (e.g., anchors with href/title).
    All other tags and attributes are stripped to prevent XSS attacks.

    Args:
        content: Raw content string that may contain HTML

    Returns:
        Sanitized content with only allowed tags and attributes
    """
    # Apply strict allowlist: only safe tags and attributes
    return bleach.clean(
        content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )


# FastAPI Application
app = FastAPI(
    title="Blog Platform API",
    description="A monolithic blog platform with clean architecture",
    version="1.0.0",
)

# Rate Limiting Setup
# Note: For production, configure Redis-backed storage to make limits consistent across workers:
# limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Security
security = HTTPBearer()

# Load environment variables from .env file (optional, for local development)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Read JWT secret from environment variable (required)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is required. "
        "Generate a secure secret using one of these methods:\n"
        "  - Command line: openssl rand -hex 32\n"
        "  - Python: import secrets; secrets.token_urlsafe(32)\n"
        "Store it in your environment variables or .env file for local development. "
        "Keep the key secret and ensure it remains consistent across deployments."
    )


# Database session dependency
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db():
    with get_db_session() as session:
        yield session


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )
    if not JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY is not configured",
        )
    user_id = AuthenticationService.verify_jwt_token(token, JWT_SECRET_KEY)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_repo = SQLUserRepository(db)
    user = user_repo.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


# API Endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    user_repo = SQLUserRepository(db)
    user_service = UserService(user_repo)

    try:
        user = user_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing",
            )
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request, credentials: UserLogin, db: Session = Depends(get_db)
):
    """
    Login user

    Rate limiting: 5 attempts per minute per IP address to prevent brute-force attacks.
    For production, configure Redis-backed storage to make limits consistent across workers.
    """
    user_repo = SQLUserRepository(db)
    user_service = UserService(user_repo)

    user = user_service.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing",
        )
    assert JWT_SECRET_KEY is not None, "JWT_SECRET_KEY must be set"
    token = AuthenticationService.generate_jwt_token(user.id, JWT_SECRET_KEY)
    return TokenResponse(access_token=token)


@app.post("/api/articles", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new article.

    Security: User-provided title and content are sanitized to prevent XSS attacks.
    - Title: All HTML tags are stripped (plain text only)
    - Content: Only safe HTML tags and attributes are allowed (strict allowlist approach)
    """
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    article_service = ArticleService(article_repo, user_repo)

    # Sanitize user input to prevent XSS attacks
    # Title must be plain text (all HTML stripped)
    sanitized_title = sanitize_title(article_data.title)
    # Content allows only safe HTML tags/attributes (e.g., anchors with href/title)
    sanitized_content = sanitize_content(article_data.content)

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID is missing",
            )
        article = article_service.create_article(
            title=sanitized_title,
            content=sanitized_content,
            author_id=current_user.id,
            tags=article_data.tags,
        )

        if not article.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Article ID is missing",
            )
        return ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            excerpt=article.excerpt,
            slug=article.slug,
            status=article.status.value,
            author_id=article.author_id,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            tags=article.tags,
            word_count=article.word_count(),
        )
    except (ValidationError, AuthorizationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/articles", response_model=List[ArticleResponse])
async def get_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get published articles"""
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    article_service = ArticleService(article_repo, user_repo)

    if search:
        articles = article_service.search_articles(search, page, per_page)
    else:
        articles = article_service.get_published_articles(page, per_page)

    return [
        ArticleResponse(
            id=article.id or "",
            title=article.title,
            content=article.content,
            excerpt=article.excerpt,
            slug=article.slug,
            status=article.status.value,
            author_id=article.author_id,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            tags=article.tags,
            word_count=article.word_count(),
        )
        for article in articles
    ]


@app.get("/api/articles/{slug}", response_model=ArticleResponse)
async def get_article(slug: str, db: Session = Depends(get_db)):
    """Get article by slug"""
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    article_service = ArticleService(article_repo, user_repo)

    article = article_service.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not article.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article ID is missing",
        )
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        excerpt=article.excerpt,
        slug=article.slug,
        status=article.status.value,
        author_id=article.author_id,
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=article.tags,
        word_count=article.word_count(),
    )


@app.put("/api/articles/{article_id}/publish")
async def publish_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish article"""
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    article_service = ArticleService(article_repo, user_repo)

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID is missing",
            )
        article_service.publish_article(article_id, current_user.id)
        return {"message": "Article published successfully"}
    except (ValidationError, AuthorizationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/articles/{article_id}/comments", response_model=CommentResponse)
async def add_comment(
    article_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add comment to article"""
    comment_repo = SQLCommentRepository(db)
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    comment_service = CommentService(comment_repo, article_repo, user_repo)

    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID is missing",
            )
        comment = comment_service.add_comment(
            article_id=article_id,
            content=comment_data.content,
            author_id=current_user.id,
            parent_id=comment_data.parent_id,
        )

        if not comment.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Comment ID is missing",
            )
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            author_id=comment.author_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/articles/{article_id}/comments", response_model=List[CommentResponse])
async def get_comments(article_id: str, db: Session = Depends(get_db)):
    """Get article comments"""
    comment_repo = SQLCommentRepository(db)
    article_repo = SQLArticleRepository(db)
    user_repo = SQLUserRepository(db)
    comment_service = CommentService(comment_repo, article_repo, user_repo)

    comments = comment_service.get_article_comments(article_id)

    return [
        CommentResponse(
            id=comment.id or "",
            content=comment.content,
            article_id=comment.article_id,
            author_id=comment.author_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
        )
        for comment in comments
    ]


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


# =============================================================================
# APPLICATION SETUP AND TESTING
# =============================================================================


def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)


def main():
    """Initialize and run the application"""
    print("🏗️ Blog Platform Monolithic Architecture Demo")
    print("=" * 60)

    # Create database tables
    create_tables()

    print("✅ Database tables created")
    print("✅ Application initialized")
    print("\n📚 Available API Endpoints:")
    print("POST /api/auth/register - Register new user")
    print("POST /api/auth/login - Login user")
    print("POST /api/articles - Create article")
    print("GET /api/articles - Get published articles")
    print("GET /api/articles/{slug} - Get article by slug")
    print("PUT /api/articles/{id}/publish - Publish article")
    print("POST /api/articles/{id}/comments - Add comment")
    print("GET /api/articles/{id}/comments - Get comments")
    print("GET /health - Health check")

    print("\n🚀 Start server with: uvicorn __main__:app --reload")
    print("📖 API docs available at: http://localhost:8000/docs")

    # Demonstrate core functionality
    demonstrate_core_functionality()


def demonstrate_core_functionality():
    """Demonstrate core functionality without web server"""
    print("\n🧪 Testing Core Functionality")
    print("-" * 40)

    with get_db_session() as db:
        # Initialize repositories
        user_repo = SQLUserRepository(db)
        article_repo = SQLArticleRepository(db)
        comment_repo = SQLCommentRepository(db)

        # Initialize services
        user_service = UserService(user_repo)
        article_service = ArticleService(article_repo, user_repo)
        comment_service = CommentService(comment_repo, article_repo, user_repo)

        try:
            # Test user registration
            print("👤 Creating test user...")
            user = user_service.register_user(
                username="testauthor",
                email="test@example.com",
                password="password123",
                first_name="Test",
                last_name="Author",
            )
            print(f"✅ User created: {user.username} ({user.email})")

            # Upgrade user to author
            user.role = UserRole.AUTHOR
            user_repo.save(user)
            print(f"✅ User promoted to: {user.role.value}")

            # Test article creation
            print("\n📝 Creating test article...")
            if not user.id:
                print("❌ User ID is missing, skipping article creation")
                return
            article = article_service.create_article(
                title="My First Blog Post",
                content="This is the content of my first blog post. It's quite exciting!",
                author_id=user.id,
                tags=["python", "tutorial", "blog"],
            )
            print(f"✅ Article created: {article.title} (slug: {article.slug})")

            # Test article publishing
            print("\n📤 Publishing article...")
            if not article.id:
                print("❌ Article ID is missing, skipping publishing")
                return
            published_article = article_service.publish_article(article.id, user.id)
            print(f"✅ Article published: {published_article.status.value}")

            # Test comment creation
            print("\n💬 Adding comment...")
            comment = comment_service.add_comment(
                article_id=article.id,
                content="Great article! Very informative.",
                author_id=user.id,
            )
            print(f"✅ Comment added: {comment.content[:50]}...")

            # Test article search
            print("\n🔍 Testing search...")
            search_results = article_service.search_articles("blog")
            print(f"✅ Found {len(search_results)} articles matching 'blog'")

            # Test getting published articles
            print("\n📚 Getting published articles...")
            published = article_service.get_published_articles()
            print(f"✅ Found {len(published)} published articles")

            # Test getting article comments
            print("\n💭 Getting article comments...")
            if not article.id:
                print("❌ Article ID is missing, skipping comment retrieval")
                return
            comments = comment_service.get_article_comments(article.id)
            print(f"✅ Found {len(comments)} approved comments")

            print("\n" + "=" * 60)
            print("🎉 Core Functionality Test Complete!")
            print("\nArchitecture Layers Demonstrated:")
            print("✅ Domain Layer - Entities, Value Objects, Domain Services")
            print("✅ Application Layer - Use Cases, Application Services")
            print("✅ Infrastructure Layer - Repositories, Database Access")
            print("✅ Presentation Layer - API Endpoints, Request/Response Models")

            print("\nMonolithic Architecture Benefits:")
            print("🚀 Single deployment unit")
            print("🚀 Simplified development and testing")
            print("🚀 ACID transactions across all operations")
            print("🚀 Consistent data model")
            print("🚀 Easy debugging and monitoring")

        except Exception as e:
            print(f"❌ Error during demonstration: {e}")


if __name__ == "__main__":
    main()
