# button.py
import discord

class ForestSessionView(discord.ui.View):
    def __init__(self, initial_creator: discord.Member, session_message_id: int):
        super().__init__(timeout=180) 
        
        self.initial_creator = initial_creator 
        self.joined_users = [initial_creator] 
        self.session_message_id = session_message_id 
        self.session_started = False 

        # --- "I'm in!" Button ---
        # The custom_id will be fully constructed after the message is sent.
        # We define a placeholder here, and update it in the forest function.
        self.join_button = discord.ui.Button(
            label="I'm in!", 
            style=discord.ButtonStyle.green, 
            custom_id=f"join_forest_session_PLACEHOLDER" # Use placeholder
        )
        self.join_button.callback = self.handle_join_button_click
        self.add_item(self.join_button)

        # --- "Start session" Button ---
        # Same for the start button custom_id
        self.start_button = discord.ui.Button(
            label="Start session",
            style=discord.ButtonStyle.primary,
            custom_id=f"start_forest_session_PLACEHOLDER" # Use placeholder
        )
        self.start_button.callback = self._start_session_callback
        self.add_item(self.start_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if the session has already started (applies to all buttons)
        if self.session_started:
            await interaction.response.send_message("This session has already started and is no longer interactive.", ephemeral=True)
            return False

        # ONLY check authorization if it's the "Start session" button being clicked
        # The custom_id IS available on the interaction object when interaction_check is called.
        if interaction.custom_id == f"start_forest_session_{self.session_message_id}":
            if interaction.user.id == self.initial_creator.id:
                return True # Authorized to click "Start session"
            else:
                await interaction.response.send_message(
                    "You are not authorized to start this session.",
                    ephemeral=True 
                )
                return False # Not authorized
        
        # For all other buttons (like "I'm in!"), if the session hasn't started, allow interaction.
        return True

    async def handle_join_button_click(self, interaction: discord.Interaction):
        # Your existing join logic
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
        await interaction.message.edit(embed=current_embed, view=self)

    async def _start_session_callback(self, interaction: discord.Interaction):
        # This callback is only reached if interaction_check allowed it (i.e., authorized user)
        if self.session_started:
            await interaction.response.send_message("The session has already been started!", ephemeral=True)
            return

        self.session_started = True

        await interaction.response.send_message(
            f"🌲 **{self.initial_creator.mention} has started the Forest session! The session message will now be removed.** 🌲",
            ephemeral=False
        )

        try:
            await interaction.message.delete()
        except discord.NotFound:
            print(f"Attempted to delete message {interaction.message.id} but it was not found.")
        except discord.Forbidden:
            print(f"Bot lacks permissions to delete message {interaction.message.id}.")
            await interaction.channel.send("Error: I do not have permissions to delete the session message.")
        
        self.stop()