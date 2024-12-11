from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from app.core.constants import UserRole, TransactionType, INITIAL_GIVEABLE_POINTS, INITIAL_REDEEMABLE_POINTS

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    users = relationship("User", back_populates="company")

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(String(60), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    role = Column(String(10), nullable=False)
    giveable_points = Column(Integer, nullable=False, default=INITIAL_GIVEABLE_POINTS)
    redeemable_points = Column(Integer, nullable=False, default=INITIAL_REDEEMABLE_POINTS)
    deleted_at = Column(DateTime(timezone=True))

    company = relationship("Company", back_populates="users")
    sent_transactions = relationship("PointsTransaction", back_populates="sender", foreign_keys="PointsTransaction.sender_id")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    __table_args__ = (
        CheckConstraint(f"role IN ('admin', 'member')", name="valid_role"),
        CheckConstraint("giveable_points >= 0", name="positive_giveable_points"),
        CheckConstraint("redeemable_points >= 0", name="positive_redeemable_points"),
    )

class PointsTransaction(Base, TimestampMixin):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(String(20), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    points = Column(Integer, nullable=False)
    admin_notes = Column(Text)

    sender = relationship("User", back_populates="sent_transactions", foreign_keys=[sender_id])
    recipients = relationship("PointsRecipient", back_populates="transaction")
    post = relationship("Post", back_populates="transactions")
    comment = relationship("Comment", back_populates="transactions")

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('recognition', 'admin_adjustment', 'initial_allocation', 'comment_recognition')",
            name="valid_transaction_type"
        ),
        CheckConstraint("points > 0", name="positive_points"),
    )

class PointsRecipient(Base, TimestampMixin):
    __tablename__ = "points_recipients"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("points_transactions.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    points_amount = Column(Integer, nullable=False)

    transaction = relationship("PointsTransaction", back_populates="recipients")
    recipient = relationship("User")

    __table_args__ = (
        CheckConstraint("points_amount > 0", name="positive_points_amount"),
    )

class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    total_points = Column(Integer, nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")
    transactions = relationship("PointsTransaction", back_populates="post")

    __table_args__ = (
        CheckConstraint("total_points > 0", name="positive_total_points"),
    )

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    total_points = Column(Integer, default=0)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    likes = relationship("CommentLike", back_populates="comment")
    transactions = relationship("PointsTransaction", back_populates="comment")

    __table_args__ = (
        CheckConstraint("total_points >= 0", name="non_negative_total_points"),
    )

class PostLike(Base, TimestampMixin):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    post = relationship("Post", back_populates="likes")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="unique_post_like"),
    )

class CommentLike(Base, TimestampMixin):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey("comments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    comment = relationship("Comment", back_populates="likes")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="unique_comment_like"),
    ) 