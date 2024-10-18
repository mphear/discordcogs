from .gemini import GoogleGemini

async def setup(bot):
    await bot.add_cog(GoogleGemini(bot))
