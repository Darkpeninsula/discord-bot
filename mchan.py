import discord
import asyncio
import pickle

perm_channels = ['CS:GO','Overwatch','Discussion: Greek','Discussion: English','Sicrit Club']

class VoiceChannel:
    def __init__(self):
        self.owner = ""
        self.chanid = 0
        #self.roleid = 0

    def setOwner(self, user):
        self.owner = user

    def setID(self, cid):
        self.chanid = cid

with open('voice_channels', 'rb') as f:
    try:
        voice_channels = pickle.load(f)
    except EOFError:
        voice_channels = []

def get_voice_channel(cid):
    for channel in voice_channels:
        if channel.chanid == cid:
            return channel

async def cchannel(message, client):
    while True:
        await client.send_typing(message.channel)

        if '"' in message.content:
            parse = message.content.split('"')
            for i in range(0, len(parse)):
                parse[i] = parse[i].rstrip().lstrip()
        else:
            parse = message.content.split()

        try:
            game = parse[1]
        except IndexError:
            await client.send_message(message.channel, 'Please specify a name for the channel (in lowercase.)')
            break

        try:
            lim = parse[2]
        except IndexError:
            lim = 'null'

        if not '"' in message.content:
            game = game.title()

        if game.lower() == 'current' and str(message.author.game) == 'None':
            await client.send_message(message.channel, 'Please launch a game then call the command again. Alternatively, provide a name.')
            break
        elif game.lower() == 'Current'.lower():
            game = str(message.author.game)

        if game.lower() == 'Counter-Strike: Global Offensive'.lower():
            game = 'CS:GO'

        exist = sum(c.name.startswith(game) for c in message.server.channels)
        num = str(exist + 1)
        #pos = sum(c.type == discord.ChannelType.voice for c in message.server.channels)

        if exist != 0:
            game += ' #%s' % num

        if str(lim) == 'cslobby':
            limit = 5
        elif str(lim) == 'owlobby':
            limit = 6
        elif str(lim).isdigit():
            limit = int(lim)
        else:
            limit = 0

        if str(lim) == 'private':
            everyone = discord.PermissionOverwrite(connect=False)
            ownerperms = discord.PermissionOverwrite(connect=True)
            channel = await client.create_channel(message.server, game, (message.server.default_role, everyone), (message.author, ownerperms), type=discord.ChannelType.voice)
        else:
            channel = await client.create_channel(message.server, game, type=discord.ChannelType.voice)

        listing = VoiceChannel()
        listing.setOwner(message.author)
        listing.setID(channel.id)
        voice_channels.append(listing)

        with open('voice_channels', 'wb') as f:
            pickle.dump(voice_channels, f)

        await client.edit_channel(channel, bitrate=96000, user_limit=limit)
        #await client.move_channel(channel, pos)
        await client.send_message(message.channel, 'Successfully created the voice channel')
        break

async def dchannel(message, client):
    while True:
        await client.send_typing(message.channel)
        parse = message.content.split(' ', 1)
        try:
            name = parse[1]
        except IndexError:
            name = 'null'
            await client.send_message(message.channel, 'No channel specified')
            break

        if name in perm_channels:
            await client.send_message(message.channel, "You don't have permission to delete that channel.")
            break

        try:
            chan = discord.utils.get(message.server.channels, name=name, type=discord.ChannelType.voice)
            channel = get_voice_channel(chan.id)

            if message.author == channel.owner:
                await client.delete_channel(chan)
                voice_channels.remove(channel)
                with open('voice_channels', 'wb') as f:
                    f.truncate()
                    pickle.dump(voice_channels, f)

                await client.send_message(message.channel, 'Successfully deleted the voice channel')
                break
            else:
                await client.send_message(message.channel, "You can only delete your channels.")
                break

        except AttributeError:
            await client.send_message(message.channel, 'Channel not found')
            break

async def echannel(message, client):
    while True:
        await client.send_typing(message.channel)
        parse = message.content.split(' ', 1)
        try:
            name = parse[1]
        except IndexError:
            await client.send_message(message.channel, 'No channel specified')
            break

        if name in perm_channels:
            await client.send_message(message.channel, "You don't have permission to edit that channel.")
            break

        try:
            chan = discord.utils.get(message.server.channels, name=name, type=discord.ChannelType.voice)
            channel = get_voice_channel(chan.id)
            if message.author == channel.owner:
                await client.send_message(message.channel, "Waiting for an edit command... *(use `$help echannel` for more info)*:")
                msg = await client.wait_for_message(author=message.author, channel=message.channel)

                response = msg.content.split(' ', 1)
                success = 'Successfully edited the voice channel'

                if response[0] == '#name':
                    try:
                        nname = response[1]
                        await client.edit_channel(chan, name=nname)
                        await client.send_message(message.channel, success)
                        break
                    except IndexError:
                        await client.send_message(message.channel, 'No new name specified.')
                        break
                elif response[0] == '#limit':
                    try:
                        limit = int(response[1])
                        await client.edit_channel(chan, user_limit=limit)
                        await client.send_message(message.channel, success)
                        break
                    except IndexError:
                        await client.send_message(message.channel, 'No limit specified.')
                        break
                elif response[0] == '#setowner':
                    try:
                        owner = response[1].lower()
                        nowner = discord.utils.find(lambda o: o.name.lower() == owner, message.channel.server.members)
                        channel.setOwner(nowner)
                        await client.send_message(message.channel, success)
                        break
                    except IndexError:
                        await client.send_message(message.channel, 'No new owner specified.')
                        break
                    except AttributeError:
                        await client.send_message(message.channel, 'No user found')
                        break
                elif response[0] == '#whitelist':
                    try:
                        arg = response[1].lower()
                        person = discord.utils.find(lambda o: o.name.lower() == arg, message.channel.server.members)
                        perms = discord.PermissionOverwrite(connect=True)
                        await client.edit_channel_permissions(chan, person, perms)
                        await client.send_message(message.channel, success)
                        break
                    except IndexError:
                        await client.send_message(message.channel, 'No user to whitelist.')
                elif response[0].startswith('#'):
                    await client.send_message(message.channel, 'Invalid edit command.')
                    break
                else:
                    break
            else:
                await client.send_message(message.channel, "You can only edit your channels.")
                break
        except AttributeError:
            await client.send_message(message.channel, 'Channel not found')
            break
