import sqlite3
from typing import Callable, Any
from functools import wraps

import discord

import breadcord
from breadcord.module import ModuleCog


class PermissionsCog(ModuleCog):
    def __init__(self, module_id: str):
        super().__init__(module_id)

        self._connection = sqlite3.connect(self.module.storage_path / "permissions.db")
        self._cursor = self._connection.cursor()
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS permissions ("
            "   permission_name TEXT PRIMARY KEY NOT NULL UNIQUE,"
            "   users TEXT NOT NULL,"
            "   roles TEXT NOT NULL"
            ")"
        )
        self.module_id = module_id

    def _check_module(self, permission_name: str, allow_all: bool) -> bool:
        if self.module_id == "no_bread":
            return False
        if allow_all and permission_name == "*":
            return False
        if permission_name.startswith(self.module_id):
            return False

        return True

    def create_permissions(self, permission_name: str) -> str:
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")
        print(self.module_id)

        if self._cursor.execute("SELECT permission_name FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone():
            return permission_name

        self._cursor.execute(
            "INSERT INTO permissions (permission_name, users, roles) VALUES (?, ?, ?)",
            (permission_name, "", "")
        )
        self._connection.commit()
        return permission_name

    def delete_permissions(self, permission_name: str) -> None:
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")

        self._cursor.execute("DELETE FROM permissions WHERE permission_name = ?", (permission_name,))
        self._connection.commit()

    def add_user(self, permission_name: str, user_id: int) -> None:
        user_id = str(user_id)
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")

        users = self._cursor.execute("SELECT users FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if users is None:
            users = []
        else:
            users = users[0].split(",")
        if user_id in users:
            return
        users.append(user_id)
        users = ",".join(users)
        self._cursor.execute("UPDATE permissions SET users = ? WHERE permission_name = ?", (users, permission_name))
        self._connection.commit()

    def remove_user(self, permission_name: str, user_id: int) -> None:
        user_id = str(user_id)
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")

        users = self._cursor.execute("SELECT users FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if users is None:
            users = []
        else:
            users = users[0].split(",")
        users.remove(user_id)
        users = ",".join(users)
        self._cursor.execute("UPDATE permissions SET users = ? WHERE permission_name = ?", (users, permission_name))
        self._connection.commit()

    def add_role(self, permission_name: str, role_id: int) -> None:
        role_id = str(role_id)
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")

        roles = self._cursor.execute("SELECT roles FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if roles is None:
            roles = []
        else:
            roles = roles[0].split(",")
        if role_id in roles:
            return
        roles.append(role_id)
        roles = ",".join(roles)
        self._cursor.execute("UPDATE permissions SET roles = ? WHERE permission_name = ?", (roles, permission_name))
        self._connection.commit()

    def remove_role(self, permission_name: str, role_id: int) -> None:
        user_id = str(role_id)
        if self._check_module(permission_name, False):
            raise ValueError("Permission name must start with module id")

        roles = self._cursor.execute("SELECT roles FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if roles is None:
            roles = []
        else:
            roles = roles[0].split(",")
        roles.remove(role_id)
        roles = ",".join(roles)
        self._cursor.execute("UPDATE permissions SET roles = ? WHERE permission_name = ?", (roles, permission_name))
        self._connection.commit()

    def get_users(self, permission_name: str) -> list[int]:
        if self._check_module(permission_name, True):
            raise ValueError("Permission name must start with module id")

        users = self._cursor.execute("SELECT users FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if users is None:
            users = []
        else:
            users = users[0].split(",")
        return users

    def get_roles(self, permission_name: str) -> list[int]:
        if self._check_module(permission_name, True):
            raise ValueError("Permission name must start with module id")

        roles = self._cursor.execute("SELECT roles FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()
        if roles is None:
            roles = []
        else:
            roles = roles[0].split(",")
        return roles

    def contains_permission(self, permission_name: str, user: discord.Member) -> bool:
        if self._check_module(permission_name, True):
            raise ValueError("Permission name must start with module id or \"*\"")

        # Admin Permissions

        users = self._cursor.execute("SELECT users FROM permissions WHERE permission_name = ?", ("*.admin",)).fetchone()

        if users is None:
            return False
        else:
            users = users[0]

        users = users.split(",") if users else []
        if str(user.id) in users:
            return True

        # General Permissions

        users = self._cursor.execute("SELECT users FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()

        if users is None:
            return False
        else:
            users = users[0]

        users = users.split(",") if users else []
        if str(user.id) in users:
            return True

        roles = self._cursor.execute("SELECT roles FROM permissions WHERE permission_name = ?", (permission_name,)).fetchone()[0]
        roles = roles.split(",") if roles else []
        for role in user.roles:
            if str(role.id) in roles:
                return True

    def list_permissions(self) -> list[str]:
        return [x[0] for x in self._cursor.execute("SELECT permission_name FROM permissions").fetchall()]

    def get_user_permissions(self, user: discord.Member) -> list[str]:
        permissions = []
        for permission in self.list_permissions():
            if self.contains_permission(permission, user):
                permissions.append(permission)
        return permissions

    @staticmethod
    def has_permission(permission_name) -> Callable:
        def decorator(func) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> None:
                if args[0].contains_permission(permission_name, args[1].user):
                    await func(*args, **kwargs)
                else:
                    embed = discord.Embed(title="Permission Denied", description=f"You don't have the `{permission_name} permission!`", color=discord.Color.red())
                    await args[1].response.send_message(embed=embed, ephemeral=True)
            return wrapper
        return decorator
