from typing import List

import discord
from discord import ui

from config import MAX_ATTACKS_PER_SESSION
from models.core import Attack


class AttackSelectMenu(ui.View):
    def __init__(
        self,
        choices: List[Attack],
    ):
        super().__init__()

        max_values = min(len(choices), MAX_ATTACKS_PER_SESSION)
        # they may have more than 10 attacks
        # since we allow 25 attacks per user

        select = ui.Select(
            min_values=1,
            max_values=max_values,
            options=[
                discord.SelectOption(
                    label=attack.name,
                    value=attack._id,
                    description=attack.description
                )
                for attack in choices
            ]
        )
        select.callback = self._select_callback
        self.select = select
        self.add_item(select)

        self.loaded_attacks = choices
        self.chosen_attacks = None

    async def _select_callback(self, interaction: discord.Interaction):
        self.chosen_attacks = [
            discord.utils.find(lambda m: m._id == value, self.loaded_attacks)
            for value in self.select.values
        ]
        await interaction.response.send_message(self.chosen_attacks)

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Select Attacks",
            description=(
                "Select the attacks you want to use in this battle. "
                "Choose wisely! You won't get to re-select them.\n\n"
                f"You'll get to select up to {MAX_ATTACKS_PER_SESSION} attacks."
            ),
            colour=discord.Colour.greyple()
        )
        return embed
    

