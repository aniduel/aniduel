import traceback

import discord
from discord import ui


CORE_CODE = """
async def _run_code():
    try:
        {code}
    except Exception as exc:
        await _log_error(exc)

import asyncio
asyncio.create_task(_run_code())
"""


class EvalModal(ui.Modal, title="Evaluate Code"):
    code = ui.TextInput(
        label="Code",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        async def _log_error(exc):
            _type = type(exc)
            trace = exc.__traceback__
            error = traceback.format_exception(_type, exc, trace)
            traceback_text = "".join(error)
            await interaction.followup.send(
                "Error occured while running:\n\n{}"
                .format(f"```sh\n{traceback_text}\n```"),
                ephemeral=True
            )

        scope = {
            "discord": discord,
            "bot": interaction.client,
            "interaction": interaction,
            "_log_error": _log_error
        }
        try:
            _to_exec = CORE_CODE.format(code=self.code.value)
            exec(_to_exec, scope, scope)
        except Exception as exc:
            await _log_error(exc)
        else:
            await interaction.followup.send(
                ":white_check_mark: Exec completed",
                ephemeral=True
            )
