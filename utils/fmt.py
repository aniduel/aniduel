import discord


def stripe_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Purchase Acknowledged",
        description=(
            "Hey there, thanks a lot for your purchase! "
            "Your `{items}` will show up in your account soon! "
            "Continue fighting summoner!"
        ),
        colour=discord.Colour.blurple()
    )
    embed.set_image(
        url="https://media.discordapp.net/attachments/993541228970917990/1012036162883424367/5a90312d7f96951c82922878.png"
    )
    return embed