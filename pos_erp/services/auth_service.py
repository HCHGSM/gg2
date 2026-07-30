import bcrypt
from datetime import datetime
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import User, AuditLog

class AuthService:
    @staticmethod
    def authenticate(username, password):
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return None, "اسم المستخدم غير موجود"
            if not user.is_active:
                return None, "الحساب معطل، يرجى مراجعة الإدارة"
            
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                user.last_login = datetime.utcnow()
                session.commit()
                # Log action
                log = AuditLog(user_id=user.id, action='LOGIN', details=f"User {username} logged in successfully")
                session.add(log)
                session.commit()
                return user, "تم تسجيل الدخول بنجاح"
            else:
                return None, "كلمة المرور غير صحيحة"
        except Exception as e:
            return None, f"خطأ في المصادقة: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        session = SessionLocal()
        try:
            user = session.query(User).get(user_id)
            if not user:
                return False, "المستخدم غير موجود"
            if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return False, "كلمة المرور الحالية غير صحيحة"
            
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password_hash = hashed
            session.commit()
            return True, "تم تغيير كلمة المرور بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
