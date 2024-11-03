import asyncio
from datetime import datetime
from discord import Enum
from discord.ext import commands


class PremiumUltimateViewData:
    def __init__(self, user, timestamp, isPremium):
        self.votes = {"yes": 0, "no": 0}
        self.user = user
        self.description = f"Should {user.mention} have the **{'Premium' if isPremium else 'Ultimate'}** role?"
        self.timestamp = timestamp
        self.isPremium = isPremium


class MemberOrRoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        # Attempt to convert to Member
        try:
            member = await commands.MemberConverter().convert(ctx, argument)
            return member
        except commands.MemberNotFound:
            pass

        # Attempt to convert to Role
        try:
            role = await commands.RoleConverter().convert(ctx, argument)
            return role
        except commands.RoleNotFound:
            pass

        # If both conversions fail, raise an error
        return None

async def schedule(task_func, run_at):
        now = datetime.now()
        wait_time = (run_at - now).total_seconds()

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            await task_func()
        else:
            await task_func()
            print(f"Schedulced time {run_at} is in the past. Task will run imediatly.")


NOTIFICATION_TEMPLATES = [
    "🛡️ Get ready to channel your inner Steve!{time_left} , the PvP tournament begins. May your aim be true and your health bar plentiful! 🍗💪",
    "🚨 Just a friendly reminder!{time_left} , the ultimate PvP showdown begins! Dust off your armor and get ready to show off those PvP skills! 💥",
    "👑 Calling all champions!{time_left} , we’ll see who claims the crown in today’s PvP tournament! Get hyped and maybe do a little victory dance while you wait! 💃🕺",
    "⚔️ Ding ding! It's almost showtime! In {time_left} , prepare to showcase your skills in the PvP tournament! Practice your best battle cry! (ROAR! 🦁)"
]

class Proxy(Enum):
    EU = "EU"
    NA = "NA"
    AS = "AS"

class Gamemode(Enum):
    FIREBALLFIGHT = "Fireballfight"
    SUMO = "Sumo"