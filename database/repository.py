import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from database.connection import SessionLocal
from database.models import (
    UserModel,
    ConversationModel,
    MessageModel,
    MemoryModel,
    ProfileModel,
    TaskModel,
    TaskStepModel,
    ResearchSourceModel,
    FileMetadataModel,
    JobModel,
    utc_now_iso,
)

logger = logging.getLogger(__name__)

class UserRepository:
    @staticmethod
    def create_user(username: str, password_hash: str) -> UserModel:
        db = SessionLocal()
        try:
            user = UserModel(username=username.strip().lower(), password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

    @staticmethod
    def get_by_id(user_id: str) -> Optional[UserModel]:
        db = SessionLocal()
        try:
            return db.query(UserModel).filter(UserModel.id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def get_by_username(username: str) -> Optional[UserModel]:
        if not username:
            return None
        db = SessionLocal()
        try:
            return db.query(UserModel).filter(UserModel.username == username.strip().lower()).first()
        finally:
            db.close()

    @staticmethod
    def update_password(username: str, password_hash: str) -> UserModel:
        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.username == username.strip().lower()).first()
            if user:
                user.password_hash = password_hash
                db.commit()
                db.refresh(user)
                return user
            else:
                user = UserModel(username=username.strip().lower(), password_hash=password_hash)
                db.add(user)
                db.commit()
                db.refresh(user)
                return user
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

class ConversationRepository:
    @staticmethod
    def create_or_get_conversation(session_id: str, user_id: str, title: str = "New Conversation") -> ConversationModel:
        db = SessionLocal()
        try:
            conv = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
            if not conv:
                conv = ConversationModel(session_id=session_id, user_id=user_id, title=title)
                db.add(conv)
                db.commit()
                db.refresh(conv)
            return conv
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

    @staticmethod
    def update_conversation_title(session_id: str, title: str) -> None:
        db = SessionLocal()
        try:
            conv = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
            if conv:
                conv.title = title
                conv.updated_at = utc_now_iso()
                db.commit()
        except Exception as exc:
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_user_conversations(user_id: str) -> List[ConversationModel]:
        db = SessionLocal()
        try:
            return (
                db.query(ConversationModel)
                .filter(ConversationModel.user_id == user_id)
                .order_by(ConversationModel.updated_at.desc())
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def save_message(session_id: str, role: str, content: str) -> MessageModel:
        db = SessionLocal()
        try:
            msg = MessageModel(session_id=session_id, role=role, content=content)
            db.add(msg)

            # Update conversation timestamp
            conv = db.query(ConversationModel).filter(ConversationModel.session_id == session_id).first()
            if conv:
                conv.updated_at = utc_now_iso()
                if conv.title == "New Conversation" and role == "user" and content:
                    conv.title = content[:30] + ("..." if len(content) > 30 else "")

            db.commit()
            db.refresh(msg)
            return msg
        except Exception as exc:
            db.rollback()
            logger.warning("Failed to save message to database: %s", exc)
            return MessageModel(session_id=session_id, role=role, content=content)
        finally:
            db.close()

    @staticmethod
    def get_session_messages(session_id: str) -> List[MessageModel]:
        db = SessionLocal()
        try:
            return (
                db.query(MessageModel)
                .filter(MessageModel.session_id == session_id)
                .order_by(MessageModel.created_at.asc())
                .all()
            )
        finally:
            db.close()

class MemoryRepository:
    @staticmethod
    def save_memory(
        user_id: str,
        content: str,
        memory_type: str = "preference",
        importance: int = 3,
        id: Optional[str] = None,
    ) -> MemoryModel:
        db = SessionLocal()
        try:
            mem = MemoryModel(
                id=id or str(uuid.uuid4()),
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
            )
            db.add(mem)
            db.commit()
            db.refresh(mem)
            return mem
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

    @staticmethod
    def update_memory(memory_id: str, user_id: str, content: str, importance: int = 3) -> Optional[MemoryModel]:
        db = SessionLocal()
        try:
            mem = db.query(MemoryModel).filter(MemoryModel.id == memory_id, MemoryModel.user_id == user_id).first()
            if mem:
                mem.content = content
                mem.importance = importance
                mem.created_at = utc_now_iso()
                db.commit()
                db.refresh(mem)
            return mem
        except Exception as exc:
            db.rollback()
            return None
        finally:
            db.close()

    @staticmethod
    def get_user_memories(user_id: str, limit: int = 50) -> List[MemoryModel]:
        db = SessionLocal()
        try:
            return (
                db.query(MemoryModel)
                .filter(MemoryModel.user_id == user_id)
                .order_by(MemoryModel.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def delete_memory(memory_id: str, user_id: str) -> bool:
        db = SessionLocal()
        try:
            mem = db.query(MemoryModel).filter(MemoryModel.id == memory_id, MemoryModel.user_id == user_id).first()
            if mem:
                db.delete(mem)
                db.commit()
                return True
            return False
        except Exception as exc:
            db.rollback()
            return False
        finally:
            db.close()

class JobRepository:
    @staticmethod
    def create_job(user_id: str, session_id: str, job_type: str) -> JobModel:
        db = SessionLocal()
        try:
            job = JobModel(user_id=user_id, session_id=session_id, job_type=job_type, status="pending", progress=0)
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            db.close()

    @staticmethod
    def update_job(
        job_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[JobModel]:
        db = SessionLocal()
        try:
            job = db.query(JobModel).filter(JobModel.id == job_id).first()
            if job:
                if status is not None:
                    job.status = status
                    if status == "running" and not job.started_at:
                        job.started_at = utc_now_iso()
                    elif status in {"completed", "failed", "cancelled"}:
                        job.completed_at = utc_now_iso()
                if progress is not None:
                    job.progress = max(0, min(100, progress))
                if result is not None:
                    job.result = result
                if error is not None:
                    job.error = error

                db.commit()
                db.refresh(job)
            return job
        except Exception as exc:
            db.rollback()
            return None
        finally:
            db.close()

    @staticmethod
    def get_job(job_id: str) -> Optional[JobModel]:
        db = SessionLocal()
        try:
            return db.query(JobModel).filter(JobModel.id == job_id).first()
        finally:
            db.close()

    @staticmethod
    def get_user_jobs(user_id: str) -> List[JobModel]:
        db = SessionLocal()
        try:
            return (
                db.query(JobModel)
                .filter(JobModel.user_id == user_id)
                .order_by(JobModel.created_at.desc())
                .all()
            )
        finally:
            db.close()
