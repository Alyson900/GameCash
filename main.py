import asyncio
import importlib
import os
from pathlib import Path
import discord
from discord.ext import commands
from src.database import DatabaseManager


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None
        )
        
        self.db = DatabaseManager()
    
    async def setup_hook(self):
        await self.load_commands()
        await self.load_events()
        await self.tree.sync()
    
    async def load_commands(self):
        commands_path = Path("src/commands")
        for file in commands_path.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            
            relative_path = file.relative_to(commands_path.parent)
            module_path = str(relative_path).replace(os.sep, ".")[:-3]
            
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "setup"):
                    await module.setup(self)
            except Exception as e:
                print(f"Erro ao carregar {module_path}: {e}")
    
    async def load_events(self):
        events_path = Path("src/events")
        for file in events_path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            
            module_path = f"src.events.{file.stem}"
            
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "setup"):
                    await module.setup(self)
            except Exception as e:
                print(f"Erro ao carregar {module_path}: {e}")
    
    async def on_ready(self):
        print(f"Bot conectado como {self.user}")
        print(f"Em {len(self.guilds)} servidores")
        self.db.init_db()


async def main():
    bot = Bot()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN não configurado")
    
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
