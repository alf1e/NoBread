import sqlite3
import importlib
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands

import breadcord
from breadcord.modules.no_bread.PermissionsCog import PermissionsCog


class NoBread(PermissionsCog, commands.GroupCog, name="nobread"):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

        self.connection = sqlite3.connect(self.module.storage_path / "permissions.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS permissions ("
            "   permission_name TEXT PRIMARY KEY NOT NULL UNIQUE,"
            "   users TEXT NOT NULL,"
            "   roles TEXT NOT NULL"
            ")"
        )

        self.create_permissions("*.admin")

        if self.bot.settings.no_bread.include_legacy_administrators.value:
            administrators = self.bot.settings.administrators.value
            for administrator in administrators:
                self.add_user("*.admin", administrator)

    @app_commands.command(name="add_permission", description="Add a permission to a user/role")
    @PermissionsCog.has_permission(permission_name="*.admin")
    async def add_permission(self, interaction: discord.Interaction, user: Union[discord.Member, discord.Role],
                             permission_name: str):
        try:
            if isinstance(user, discord.Member):
                self.add_user(permission_name, user.id)
                embed = discord.Embed(title="Permissions Manager",
                                      description=f"➕ Added permission `{permission_name}` to {user.mention}")
            else:
                self.add_role(permission_name, user.id)
                embed = discord.Embed(title="Permissions Manager",
                                      description=f"➕ Added permission `{permission_name}` to {user.mention}")

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Permissions Manager",
                                  description=f"⚠️ Failed to add permission `{permission_name}` to {user.mention}")

    @app_commands.command(name="remove_permission", description="Remove a permission from a user/role")
    @PermissionsCog.has_permission(permission_name="*.admin")
    async def remove_permission(self, interaction: discord.Interaction, user: Union[discord.Member, discord.Role], permission_name: str):
        try:
            if isinstance(user, discord.Member):
                self.remove_user(permission_name, user.id)
                embed = discord.Embed(title="Permissions Manager",
                                      description=f"➖ Removed permission `{permission_name}` from {user.mention}")
            else:
                self.remove_role(permission_name, user.id)
                embed = discord.Embed(title="Permissions Manager",
                                      description=f"➖ Removed permission `{permission_name}` from {user.mention}")

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Permissions Manager",
                                  description=f"⚠️ Failed to remove permission `{permission_name}` from {user.mention}")

    @add_permission.autocomplete("permission_name")
    @remove_permission.autocomplete("permission_name")
    async def add_permission_name_auto_complete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=permission, value=permission)
            for permission in self.list_permissions()
            if current in permission
        ]


async def setup(bot: breadcord.Bot):
    await bot.add_cog(NoBread("no_bread"))
