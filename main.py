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
                await ctx.send(f"Error: {data.get('message', 'Unknown error')}")
        else:
            # Handle various HTTP errors
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
                    await ctx.send(f"Invalid UID: {uid}")
            elif response.status_code == 500:
                embed = discord.Embed(
                    title="Server Error",
                    description=f"**Server is experiencing issues**\nPlease try again later or check if the UID {uid} is valid.",
                    color=0xff0000
                )
                embed.set_footer(text="This might be due to invalid UID or server maintenance")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"HTTP Error: {response.status_code}")
                    
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='character')
async def get_character(ctx, uid: str, char_num: int):
    """Get detailed character info by UID and character number"""
    try:
        response = requests.get(f"{BASE_URL}/{uid}")
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'success':
                player = data['data']['player']
                characters = data['data']['characters']
                
                if char_num < 1 or char_num > len(characters):
                    await ctx.send(f"Invalid character number. Please use 1-{len(characters)}")
                    return
                
                char = characters[char_num - 1]
                
                embed = discord.Embed(
                    title=f"{char['name']} (E{char['rank']})",
                    description=f"{player['nickname']} ({player['uid']})",
                    color=0x9932cc if char['rarity'] == 5 else 0x4169e1
                )
                
                # Character basic info
                embed.add_field(
                    name="📋 Basic Info",
                    value=f"Level: {char['level']}\nPath: {char['path']['name']}\nElement: {char['element']['name']}\nRarity: {'⭐' * char['rarity']}",
                    inline=False
                )
                
                # Light Cone info
                lc = char.get('light_cone')
                if lc:
                    embed.add_field(
                        name="🔆 Light Cone",
                        value=f"**{lc['name']}** (S{lc['rank']})\nLevel: {lc['level']}\nRarity: {'⭐' * lc['rarity']}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🔆 Light Cone",
                        value="No Light Cone equipped",
                        inline=False
                    )
                
                # All Stats
                stats = char.get('final_stats', [])
                if stats:
                    stat_lines = []
                    for stat in stats:
                        if 'Base' in stat['name'] or stat['name'] == 'SPD':
                            stat_lines.append(f"{stat['name']}: {stat['value']:,}")
                        else:
                            stat_lines.append(f"{stat['name']}: {stat['value']:.1f}%")
                    
                    embed.add_field(
                        name="📊 Character Stats",
                        value="\n".join(stat_lines),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📊 Character Stats",
                        value="Stats not available",
                        inline=False
                    )
                
                # Relic Sets
                sets = char.get('relic_sets', [])
                if sets:
                    set_info = []
                    for relic_set in sets:
                        set_info.append(f"{relic_set['name']} ({relic_set['num']}pc)")
                    
                    embed.add_field(
                        name="🛡️ Relic Sets",
                        value="\n".join(set_info),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🛡️ Relic Sets",
                        value="No relic sets equipped",
                        inline=False
                    )
                
                # Relic Score
                score = char.get('relic_score')
                if score:
                    embed.add_field(
                        name="🏆 Relic Score",
                        value=f"Rank: **{score['rank']}**\nTotal: {score['total_score']}\nAverage: {score['average_score']}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🏆 Relic Score",
                        value="Relic score not available",
                        inline=False
                    )
                
                embed.set_thumbnail(url=char['portrait'])
                embed.set_footer(text="🌐 Visit our web version at https://app.hsr-profile.com/")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Error: {data.get('message', 'Unknown error')}")
        else:
            if response.status_code == 500:
                embed = discord.Embed(
                    title="Server Error",
                    description=f"**Server is experiencing issues**\nPlease try again later or check if the UID {uid} is valid.",
                    color=0xff0000
                )
                embed.set_footer(text="This might be due to invalid UID or server maintenance")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"HTTP Error: {response.status_code}")
                    
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))