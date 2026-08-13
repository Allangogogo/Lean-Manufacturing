"""
安全模块：JWT 签发/验证 + 密码哈希

职责：
1. 密码哈希与校验（bcrypt）
2. JWT Access Token 签发与验证
3. Token 过期处理
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


# ============================================================
# 密码操作
# ============================================================

def hash_password(password: str) -> str:
    """明文密码 → bcrypt 哈希。"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码是否匹配。"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ============================================================
# JWT 操作
# ============================================================

def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    签发 JWT Access Token。

    Args:
        data: Token 载荷（必须包含 sub=user_id）
        expires_delta: 自定义过期时间

    Returns:
        编码后的 JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    })
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    解码并验证 JWT Access Token。

    Returns:
        Token 载荷字典，失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """从 Token 中提取用户 ID。"""
    payload = decode_access_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (ValueError, TypeError):
        return None
