"""
小满 — MySQL 数据库连接与初始化
连接参数从环境变量读取，默认连本地
"""

import os

import pymysql
import pymysql.cursors
from pymysql.constants import FIELD_TYPE
from pymysql.converters import conversions

# MySQL DECIMAL → Python float，避免 JSON 序列化变成字符串
_conv = conversions.copy()
_conv[FIELD_TYPE.DECIMAL] = float
_conv[FIELD_TYPE.NEWDECIMAL] = float

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

DB_NAME = os.environ.get("MYSQL_DATABASE", "xiaoman")


class _DB:
    """薄封装 pymysql 连接，提供与 sqlite3 兼容的 conn.execute() 快捷方法"""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        return cur  # pymysql Cursor 支持 .fetchone() .fetchall() .lastrowid

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db() -> _DB:
    """每个请求新建连接，DictCursor 自动返回 dict"""
    return _DB(pymysql.connect(database=DB_NAME, conv=_conv, **MYSQL_CONFIG))


def init_db():
    """初始化数据库和表（启动时调用）"""
    # 先建库
    cfg = {k: v for k, v in MYSQL_CONFIG.items() if k != "database"}
    conn = pymysql.connect(**cfg)
    with conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    conn.close()

    # 建表
    db = get_db()

    # 用户表
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            username      VARCHAR(50)  NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # 业务表（重建以支持 user_id）
    db.execute("DROP TABLE IF EXISTS messages")
    db.execute("DROP TABLE IF EXISTS goals")
    db.execute("DROP TABLE IF EXISTS bills")

    db.execute("""
        CREATE TABLE bills (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT          NOT NULL,
            type        VARCHAR(10)  NOT NULL DEFAULT 'expense',
            amount      DECIMAL(10,2) NOT NULL,
            category    VARCHAR(50)  NOT NULL DEFAULT '其他',
            item        VARCHAR(200) DEFAULT '',
            date        VARCHAR(10)  NOT NULL,
            created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.execute("""
        CREATE TABLE goals (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            user_id       INT            NOT NULL,
            name          VARCHAR(100)   NOT NULL,
            target_amount DECIMAL(10,2)  NOT NULL,
            saved_amount  DECIMAL(10,2)  NOT NULL DEFAULT 0,
            completed     TINYINT        DEFAULT 0,
            created_at    TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
            completed_at  TIMESTAMP      NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.execute("""
        CREATE TABLE messages (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            user_id    INT          NOT NULL,
            role       VARCHAR(20)  NOT NULL,
            content    TEXT         NOT NULL,
            created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.close()
