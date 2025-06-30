import discord
from discord.ext import commands
import json
from groq import Groq
import random
import sys

"""
//=========//
// Helpers //
//=========//
"""
async def getUsername(userid):
    user = await client.fetch_user(userid)
    return user

def readSecrets():
    """
    Returns a dictionary
    """
    with open('secrets.json') as file:
        secrets = json.load(file)
    return secrets

async def setIdentity(userid, powerlevel = 0, money = 0, chathistory = []):
    # Getter
    try:
        with open('identity.json', 'r') as file:
            identityfile = json.load(file)
    except:
        identityfile = {}

    username = await getUsername(userid)

    #Processing
    if str(userid) not in identityfile:
        userdata = {
            'username': str(username),
            "power_level": powerlevel,
            "money": money,
            "chathistory": chathistory
        }
        identityfile[str(userid)] = userdata
    
        # Setter
        with open('identity.json', 'w') as file:
            json.dump(identityfile, file,indent=4)


async def getIdentity(userid,attempt = 0):
    try:
        with open('identity.json', 'r') as file:
            identityfile = json.load(file)
    except:
        # User is not identified
        await setIdentity(userid)
        if attempt < 2:
            getIdentity(userid, attempt = attempt+1)


    return identityfile[userid]



"""
//===============//
// Initalization //
//===============//
"""

# Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Groq
groqclient = Groq(api_key=readSecrets()["groq_token"])

"""
//==========//
// Helpers 2//
//==========//
"""

def askGroq(question):
    """
    Takes in a string and returns a string
    """
    messages = [
    {"role": "user", "content": f"{question}"}
    ]
    response = groqclient.chat.completions.create(
    model="llama3-70b-8192",
    messages=messages
    ) 
    return response.choices[0].message.content

"""
//==========//
// Commands //
//==========//
"""

class Dnd:
    def __init__(self):
        self.description = "this rolls a dice from 1-20"
        self.power = 0
    
    async def command(self, message, parameter):
        await message.channel.send(f"your number is {str(random.randrange(1,20))} cuh")
        

class Ping:
    def __init__(self):
        self.description = "replys your ping"
        self.power = 0
        
    async def command(self, message, parameter):
        latency = f"{client.latency:.2f} ms"
        await message.channel.send(f"pong {latency}")

class Commandlist:
    def __init__(self):
        self.description = "sends a list of commands"
        self.power = 0
    
    async def command(self, message, parameter):
        lisst = "```"
        for command in commands:
            lisst += f"{command} description: {commands[command].description}\n"
            #await message.channel.send(f"{command} description: {commands[command].description}")
        lisst += "```"
        await message.channel.send(lisst)

class Talk:
    def __init__(self):
        self.description = "talks with the bot using ai"
        self.power = 1

    async def command(self, message, parameter):
        groqresponse = askGroq(' '.join(parameter))
        await message.channel.send(groqresponse)

        
class Kys:
    def __init__(self):
        self.description = "turns off bot"
        self.power = 5

    async def command(self,message, parameter):
        await message.channel.send(":C")
        sys.exit()
        
commands = {
    "dnd": Dnd(),
    "ping": Ping(),
    "commands":Commandlist(),
    "talk": Talk(),
    "kys": Kys(),
}

"""
//=========//
// Invokes //
//=========//
"""

@client.event
async def on_ready():
    print(f'{client.user} is online!')

    #Registering all users

    for guild in client.guilds:
        for member in guild.members:
            await setIdentity(member.id)

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return #ignores self
    

    # Content processing
    processed_message = message.content.lower()[5::].split(" ")
    processed_command = processed_message[0]
    processed_parameters = processed_message[1::]
    if message.content.lower().startswith('carl!') and processed_command in commands.keys():

        #get user power before doing anything
        if commands[processed_command].power<=(await getIdentity(str(message.author.id)))['power_level']:
            await commands[processed_command].command(message, processed_parameters)
        else:
            await message.channel.send("You dont need the power level")
    


"""
//==============//
// Finalization //
//==============//
"""

client.run(readSecrets()["bot_token"])