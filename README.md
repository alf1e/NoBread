# No Bread!
A Breadcord module to manage permissions for your modules!

## Installation
⚠️ Module Installation is not currently a feature of Breadcord. ⚠️

## Usage
```py
import discord
from discord import app_commands
from discord.ext import commands

import breadcord
from breadcord.modules.no_bread.PermissionsCog import PermissionsCog


class Example(PermissionsCog, commands.GroupCog, name="example"):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        
        self.create_permissions("example.example")

    @app_commands.command(name="editor")
    @PermissionsCog.has_permission(permission_name="example.example")
    async def example(self, interaction: discord.Interaction):
        await interaction.response.send_message("Example!")


async def setup(bot: breadcord.Bot):
    await bot.add_cog(Example("example"))
```
This will create an example module that can only be used by users/roles with the `example.example` permission.

### Notes
- The first segment of permission name (before the first dot) **MUST** start with your module ID **OR** `*`.

## Commands
1. `/nobread add_permission user:Example permission_name:example.example`
    
    Adds the `example.example` permission to the user `Example` **OR** role `Example`.

   **Permission:** `*.admin`


2. `/nobread remove_permission user:Example permission_name:example.example`

    Removes the `example.example` permission from the user `Example` **OR** role `Example`.

   **Permission:** `*.admin`
## Feedback
If you have any feedback, please join [My Discord Server](http://go.itsmealfie0.com/discord) and share it with me!