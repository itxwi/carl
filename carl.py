import discord
from discord.ext import commands
import json
from groq import Groq
import time
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

async def setIdentity(userid, powerlevel=None, money=None, chathistory=None,lastclaimed=None, inventory = None):
    """
    Sets or updates user identity. If a value is None, keeps the old value or uses a default.
    """
    try:
        with open('identity.json', 'r') as file:
            identityfile = json.load(file)
    except Exception:
        identityfile = {}

    userid = str(userid)
    # Get old values or defaults, get(key, value if key dne)
    old = identityfile.get(userid, {})


    if powerlevel is None:
        powerlevel = old.get("power_level", 0)
    if money is None:
        money = old.get("money", 0)
    if chathistory is None:
        chathistory = old.get("chathistory", [])
    if lastclaimed is None:
        lastclaimed = old.get("lastclaimed", time.time())
    if inventory is None:
        inventory = old.get("inventory",{})

    username = str(await getUsername(userid))

    userdata = {
        'username': username,
        "power_level": powerlevel,
        "money": money,
        "chathistory": chathistory,
        "lastclaimed": lastclaimed,
        "inventory": inventory
    }

    identityfile[userid] = userdata
    with open('identity.json', 'w') as file:
        json.dump(identityfile, file, indent=4)


async def getIdentity(userid):
    userid = str(userid)
    try:
        with open('identity.json', 'r') as file:
            identityfile = json.load(file)
    except Exception:
        identityfile = {}
    if userid not in identityfile:
        # User was not registered

        await setIdentity(userid, powerlevel=0, money=0, chathistory=[], lastclaimed=0,inventory={})

        # Now reload
        with open('identity.json', 'r') as file:
            identityfile = json.load(file)
    return identityfile[userid]

async def addMoney(userid, money=0):
    user = await getIdentity(userid)
    usermoney = user["money"] + money
    await setIdentity(userid, money=usermoney)


async def removeMoney(userid, money=0):
    user = await getIdentity(userid)
    usermoney = user["money"] - money
    await setIdentity(userid, money=usermoney)

#async def setMoney(u)


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

def askGroq(question,messages = None):
    """
    Takes in a string and returns a string
    """
    if messages == None:
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
        self.power = 0

    async def command(self, message, parameter):
        chathistory = (await getIdentity(str(message.author.id)))["chathistory"]
        

                   
        question = ' '.join(parameter)
        chathistory.append(
            {
                "role": "user",
                "content": question
            }
        )

        groqresponse = askGroq(question,chathistory)
        chathistory.append(
            {
                "role": "assistant",
                "content": groqresponse
            }
        )

        
        await setIdentity(str(message.author.id),chathistory=chathistory)
        await message.channel.send(groqresponse)

        
class Kys:
    def __init__(self):
        self.description = "turns off bot"
        self.power = 5

    async def command(self,message, parameter):
        await message.channel.send(":C")
        sys.exit()

class ClearHistory():
    def __init__(self):
        self.description = "clears chat history with the bot"
        self.power = 0
    
    async def command(self,message,parameter):
        await setIdentity(message.author.id, chathistory=[])
        await message.channel.send("bonk my head hurt")

class DailyClaim():
    def __init__(self):
        self.description = "claim ur daily 500 dollar"
        self.power = 0

    async def command(self,message,parameter):
        lastclaimed = (await getIdentity(message.author.id)).get("lastclaimed",time.time())
        if time.time()-lastclaimed > 24*60*60:
            await setIdentity(message.author.id,lastclaimed=time.time()
                              )
            await addMoney(message.author.id,500)
            await message.channel.send("claimed")
        else:
            await message.channel.send(f"wait {(24*60*60)-round(time.time()-lastclaimed,1)} more seconds")

class Inventory():
    def __init__(self):
        self.description = "check inventory"
        self.power = 0
    
    async def command(self,message,parameter):
        playerinventory = (await getIdentity(message.author.id)).get("inventory", {})
        playermoney = (await getIdentity(message.author.id)).get("money", 0)

        lisst = "```"
        for item in playerinventory:
            amount = playerinventory[item]
            lisst += f"{item}: {amount} \n"
            #await message.channel.send(f"{command} description: {commands[command].description}")
        lisst+=f"\n"
        lisst+=f"amount of cash: {playermoney}"
        lisst += "```"

        await message.channel.send(lisst)

        
commands = {
    "dnd": Dnd(),
    "ping": Ping(),
    "commands":Commandlist(),
    "clearhistory": ClearHistory(),
    "talk": Talk(),
    "claim": DailyClaim(),
    "inv": Inventory(),
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

    # #Registering all users

    # for guild in client.guilds:
    #     for member in guild.members:
    #         print(member)
    #         await setIdentity(member.id,powerlevel=None,money=None,chathistory=None)

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
        userpower = (await getIdentity(str(message.author.id)))['power_level']
        if commands[processed_command].power<=userpower:
            await commands[processed_command].command(message, processed_parameters)
        else:
            await message.channel.send(f"if u a broke boy jus say so, your power is {userpower}, required power is {commands[processed_command].power}")

    # grammar correction software
    if "me and" in message.content:
        corrected_subject = askGroq(f"""
        Check the grammar of this sentence, which includes the phrase "me and ___".

        Goal:
        - Determine if "me and ___" should be corrected to "___ and I".
        - Only apply the correction if "me and ___" is used as the subject of the sentence.
        - If the phrase is used as an object (e.g., someone saw me and my friends), no correction is needed.

        Instructions:
        - If a correction is needed, return only the subject part before "I" (e.g., "my friends", "the dog and the lady").
        - If no correction is needed, return exactly: pineapple123

        Examples:
        1. "me and my friends went to the store" → my friends  
        (Because "me went to the store" is incorrect.)
        2. "me and the dog ran home" → the dog  
        (Because "me ran home" is incorrect.)
        3. "they saw me and my friends at the park" → pineapple123  
        (Because "they saw me" is correct.)
        4. "the monster was going to eat me and my friends" → pineapple123  
        (Because "eat me" is correct.)

        Respond **only** with:
        - the subject before "I" (if correction is needed), or  
        - "pineapple123" (if no correction is needed)

        Sentence: {message.content}

        Complete this sentence: "erm actually it's ____ and I"
        """)

        if "pineapple123" not in corrected_subject:
            await message.channel.send(f"erm actually its {corrected_subject} and I")


"""
//==============//
// Finalization //
//==============//
"""

client.run(readSecrets()["bot_token"])