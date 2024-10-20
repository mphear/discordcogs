import os
import random
import google.generativeai as genai
import discord
from redbot.core import commands, Config
from discord.ext.commands import has_permissions

class GoogleGemini(commands.Cog):
    """Cog to use Google Gemini API and allow dynamic API key updates."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9876543210)  # Specific unique identifier for the cog config
        default_guild = {
            "api_key": None
        }
        self.config.register_global(**default_guild)  # Register global config to store API key

    @commands.group(name="ai", invoke_without_command=True)
    async def ai(self, ctx: commands.Context, *, query: str = None):
        """
        Query the Google Gemini API with a question or statement.
        """
        if query is None:
            await ctx.send_help()  # If no subcommand or query is provided, show the help message.
            return

        # Retrieve the stored API key
        api_key = await self.config.api_key()

        if not api_key:
            await ctx.send("API key is not set. Use `!ai apikey <your_key>` to set it.")
            return

        # Configure the Gemini API with the stored API key
        genai.configure(api_key=api_key)

        # Perform the query with the user's input using GenerationConfig
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="You are a helpful assistant named Phearbot who works inside of Discord as an assistant. Answer concisely and factually, using a casual tone. You can also be sarcastic and rude if you need to be, however questions asked will remain true. Format responses in Markdown where appropriate."
            )
            response = model.generate_content(
                query,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=256,  # Set the maximum number of tokens
                    temperature=0.7,        # Control response creativity
                    candidate_count=1       # Number of responses to generate
                ),
                tools=[]  # Optional: Add any tools the model may use (e.g., function calling, code execution)
            )
            await ctx.send(response.text)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @ai.command(name="apikey")
    @has_permissions(administrator=True)  # Only allow users with administrator permissions to set the API key
    async def update_api_key(self, ctx: commands.Context, *, api_key: str = None):
        """Set or update the Google Gemini API key."""
        if api_key is None:
            await ctx.send(f"Please enter your Google Gemini API key. You can also use `{ctx.prefix}ai apikey <your_key>` directly to set it with any prefix (e.g., `!`, `!!`, `-`).")

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel

            # Wait for the user to enter the API key if not provided in the command
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                api_key = msg.content.strip()  # Waits for 60 seconds for a reply
            except Exception as e:
                await ctx.send(f"An error occurred while waiting for your input: {str(e)}")
                return

        # Store the new API key in the config
        try:
            await self.config.api_key.set(api_key)
            # Confirm if the key was saved correctly by retrieving it
            stored_api_key = await self.config.api_key()
            if stored_api_key == api_key:
                await ctx.send("API key updated successfully.")
            else:
                await ctx.send("There was an error saving the API key. Please try again.")
        except Exception as e:
            await ctx.send(f"An error occurred while saving the API key: {str(e)}")

# Setup function for Redbot to load the cog
async def setup(bot):
    await bot.add_cog(GoogleGemini(bot))
