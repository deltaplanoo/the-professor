import discord

class ForestSessionView(discord.ui.View):
    def __init__(self, initial_creator: discord.Member, session_message_id: int):
        # We're removing timeout=None because you don't care about persistence across restarts.
        # Buttons will naturally expire after a few minutes (default is 180 seconds)
        # or when the bot is restarted, which is fine for your requirement.
        super().__init__() 
        
        self.joined_users = [initial_creator] 
        self.session_message_id = session_message_id 

        # Add the button directly. The custom_id is made unique by embedding the message ID.
        self.add_item(discord.ui.Button(
            label="I'm in!", 
            style=discord.ButtonStyle.green, 
            custom_id=f"join_forest_session_{self.session_message_id}" # This MUST be unique!
        ))

    # This method defines what happens when the button is clicked.
    # It will be automatically called because we set the custom_id and add_item.
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # You can add checks here, e.g., only allow certain users to click the button.
        # For this case, we just ensure the interaction is valid.
        return True


    # This is the actual logic that the dynamically created button will execute.
    # We'll link the dynamic button's callback to this method in logic.py.
    async def handle_join_button_click(self, interaction: discord.Interaction):
        if interaction.user in self.joined_users:
            await interaction.response.send_message("You have already joined this session!", ephemeral=True)
            return

        self.joined_users.append(interaction.user)
        current_joined_count = len(self.joined_users)

        current_embed = interaction.message.embeds[0]
        current_embed.set_footer(text=f"Users in session: {current_joined_count}")

        await interaction.response.send_message(
            f"You have successfully joined the session! Current participants: {current_joined_count}",
            ephemeral=True
        )
        await interaction.message.edit(embed=current_embed)