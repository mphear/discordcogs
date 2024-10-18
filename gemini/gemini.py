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

    # Using hybrid_command allows it to work with both slash and text commands
    @commands.hybrid_command(name="ai", with_app_command=True)
    async def ai_query(self, ctx: commands.Context, *, query: str):
        """
        Query the Google Gemini API with a question or statement.
        """
        # Retrieve the stored API key
        api_key = await self.config.api_key()

        if not api_key:
            await ctx.send("API key is not set. Use `!ai apikey` to set it.")
            return

        # Configure the Gemini API with the stored API key
        genai.configure(api_key=api_key)

        # Perform the query with the user's input using GenerationConfig
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="You are a helpful assistant. Answer concisely and factually, using a friendly tone. Format responses in Markdown where appropriate."
            )
            response = model.generate_content(
                query,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=256,  # Set the maximum number of tokens
                    temperature=0.7,        # Control response creativity
                    candidate_count=1,      # Number of responses to generate
                    stop_sequences=[]        # Stop sequences if needed
                ),
                tools=[],  # Optional: Add any tools the model may use (e.g., function calling, code execution)
                safety_settings=[
                    genai.types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK"
                    ),
                    genai.types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK"
                    ),
                    genai.types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK"
                    ),
                    genai.types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK"
                    )
                ]
            )
            await ctx.send(response.text)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="apikey", aliases=['set_api_key'], invoke_without_command=True)
    @has_permissions(administrator=True)  # Only allow users with administrator permissions to set the API key
    async def update_api_key(self, ctx: commands.Context):
        """Start the process to update the Google Gemini API key."""
        await ctx.send(f"Please enter your Google Gemini API key. You can also use `{ctx.prefix}apikey <your_key>` directly to set it with any prefix (e.g., `!`, `!!`, `-`).")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        # Wait for the user to enter the API key
        try:
            if len(ctx.message.content.split()) > 1:
                new_api_key = ctx.message.content.split(' ', 1)[1]
            else:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                new_api_key = msg.content  # Waits for 60 seconds for a reply

            # Store the new API key in the config
            await self.config.api_key.set(new_api_key)

            # Confirm the API key has been updated
            await ctx.send("API key updated successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

# Setup function for Redbot to load the cog
async def setup(bot):
    # Set up intents for the bot
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True  # Required to read message content for on_message events

    bot.intents = intents
    await bot.add_cog(GoogleGemini(bot))
