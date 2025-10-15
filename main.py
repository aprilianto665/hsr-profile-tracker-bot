import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

BASE_URL = "https://hsr-backend.redfield-e7b65d33.southeastasia.azurecontainerapps.io/profile"

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')

@bot.command(name='profile')
async def get_profile(ctx, uid: str):
    """Get HSR profile by UID"""
    try:
        response = requests.get(f"{BASE_URL}/{uid}")
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'success':
                player = data['data']['player']
                characters = data['data']['characters']
                
                embed = discord.Embed(
                    title=f"🌟 {player['nickname']} (UID: {player['uid']})",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="📊 Player Info",
                    value=f"Level: {player['level']}\nWorld Level: {player['world_level']}\nFriends: {player['friend_count']}\nSignature: {player['signature'][:50]}{'...' if len(player['signature']) > 50 else ''}",
                    inline=False
                )
                
                embed.add_field(
                    name="🏆 Space Info",
                    value=f"Universe Level: {player['space_info']['universe_level']}\nAvatars: {player['space_info']['avatar_count']}\nLight Cones: {player['space_info']['light_cone_count']}\nRelics: {player['space_info']['relic_count']}\nAchievements: {player['space_info']['achievement_count']}",
                    inline=False
                )
                
                char_list = []
                for i, char in enumerate(characters, 1):
                    char_list.append(f"{i}. **{char['name']}** (Lv.{char['level']}) - E{char['rank']}")
                
                embed.add_field(
                    name="👥 Characters",
                    value="\n".join(char_list),
                    inline=False
                )
                
                embed.set_thumbnail(url=player['avatar']['icon'])
                embed.set_footer(text="🌐 Visit our web version at https://app.hsr-profile.com/")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Error: {data.get('message', 'Unknown error')}")
        else:
            # Handle invalid UID or other HTTP errors
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', 'Invalid UID')
                    
                    embed = discord.Embed(
                        title="Profile Not Found",
                        description=f"**{error_message}**\nPlease check your UID and try again.",
                        color=0xff0000
                    )
    
                    embed.set_footer(text="Make sure your profile is public and UID is correct")
                    
                    await ctx.send(embed=embed)
                except:
                    await ctx.send(f"❌ Invalid UID: {uid}")
            else:
                await ctx.send(f"❌ HTTP Error: {response.status_code}")
                    
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))