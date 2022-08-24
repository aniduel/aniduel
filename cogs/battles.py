import discord
from discord import app_commands
from discord.ext import commands

from bot import ShardedBot
from components.battles import AttackSelectMenu
from models.core import TEST_ATTACK


class Battles(commands.GroupCog, description="Battle related commands"):
    def __init__(self, bot: ShardedBot):
        self.bot = bot

    @app_commands.command(
        description="Start a duel with another member"
    )
    @app_commands.describe(member="The member you'd like to start a duel with")
    async def duel(self, interaction: discord.Interaction, member: discord.Member):
        view = AttackSelectMenu([TEST_ATTACK])
        await interaction.response.send_message(
            view=view,
            embed=view.embed,
            ephemeral=True
        )

class _FakeSelf:
    def __init__(self, bot: ShardedBot):
        self.bot = bot

@app_commands.context_menu(name="Duel")
async def ctx_duel(interaction: discord.Interaction, member: discord.Member):
    group = interaction.client.tree.get_command("battles") # type: ignore
    command = group.get_command("duel")
    _self = _FakeSelf(interaction.client) # type: ignore
    await command.callback(_self, interaction, member)

async def setup(bot: ShardedBot):
    bot.tree.add_command(ctx_duel)
    await bot.add_cog(Battles(bot))
