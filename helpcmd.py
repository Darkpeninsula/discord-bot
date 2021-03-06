import discord
import asyncio
import gc

class Command:
    def __init__(self, cdesc, cname, args, adv, example, perms):
        self.desc = cdesc
        self.name = cname
        self.args = args
        self.adv = adv
        self.example = example
        self.perms = perms

cchannel = Command(
    cdesc='Creates a channel with the `name`.',
    cname='cchannel',
    args='name;type',
    adv='`<name>` can be a single word in lowercase, any ammount of words inside "", or `current`. `current` will set the channel name to the game you are playing. `<type>` can be an intiger, `private`, `party` or `public`. If it is an intiger, that will be the client limit. If it is `private`, only whitelisted users will be able to join. To whitelist you need to do `$echannel <channel name>` and then use `#whitelist <name>`. If it is `party`, then you must specify party members in the syntax `name1;name2;name3`. It will basically automatically whitelist all the names when the channel is initialized. You can use the normal whitelist to add more members later. `public` makes it so even users without perms can join the channel (Keep in mind you could just whitelist them and they could join even without perms)',
    example='`$cchannel something 8` will return a channel named "Something" with user limit 8\n `$cchannel "Something Cool" private` will return a whitelist-only channel named "Something Cool" with unlimited user limit but whitelist only (giving a name inside "" will be the literal name of the channel)\n `$cchannel current party nondy;agouraki`, which will create a private channel with the creator, agouraki and nondy whitelisted by default.',
    perms=True
)
dchannel = Command(
    cdesc='Deletes the channel with the **exact** name',
    cname='dchannel',
    args='name',
    adv='You must be the owner of the channel to delete it.',
    example='`$dchannel Sicrit Club` (Using "" on $dchannel is optional)',
    perms=True
)
echannel = Command(
    cdesc='Edits a channel.',
    cname='echannel',
    args='name',
    adv='After calling `$echannel <channel>` the bot will wait for you to input an edit command.\n The valid edit commands are the following:\n `#name <name>` - Replaces the current channel name with the `<name>`\n `#limit <limit>` - Replaces the user limit with `<limit>`\n `#whitelist <user>` - Whitelists the `<user>` to your private channel\n `#lock` - Locks the channel, making it private, whitelisting all users already in the channel.\n `#unlock` - Unlocks the channel, deletes the whitelist, and makes it so users with perms can join.',
    example='`$echannel Sicrit Club` then after the bot responds: `#name Not Sicrit Club`',
    perms=True
)
highnoon = Command(
    cdesc="It's High Noon somewhere in the world. This command tells you where.",
    cname='highnoon',
    args='null',
    adv='null',
    example='null',
    perms=True
)
purge = Command(
    cdesc="Purges a user from a channel. (Deletes their messages)",
    cname='purge',
    args='name;limit',
    adv='Checks the last 100 messages in the channel by default. To make it look in more or less messages, just specify a `<limit>` (should be an intiger)',
    example='`$purge nondy 40`',
    perms='manage_messages'
)
mvmembers = Command(
    cdesc="Moves users to a channel.",
    cname='mvmembers',
    args='channel;members',
    adv='Members must be in the same syntax as `$cchannel something party`, so like this `nondy;rain;petergrove`',
    example='`$mvmembers CS:GO rain;agouraki;nondy;hydratec`',
    perms='move_members'
)
addwowsv = Command(
    cdesc='Whitelists the current server as a WoW server and adds WoW functionality to it.',
    cname='addwowsv',
    args='null',
    adv='Also lets the bot add a role for every class in the game.',
    example='null',
    perms='administrator'
)
wowclass = Command(
    cdesc='Sets you as the WoW class you specify.',
    cname='class',
    args='wowclass',
    adv='Only available on WoW discords.',
    example='`$class death knight`',
    perms=True
)

cmds = []

for obj in gc.get_objects():
    if isinstance(obj, Command):
        cmds.append(obj)

def get_args(cmd):
    args = cmd.args.split(';')
    args_str = ''
    for arg in args:
        if arg != 'null':
            args_str += '<{}> '.format(arg)

    return args_str

def get_cmd(cmnd):
    for cmd in cmds:
        if cmd.name == cmnd:
            return cmd

def get_perms(message, cmd):
    if type(cmd.perms) != bool:
        perms = "role.permissions." + cmd.perms
        for role in message.author.roles:
            if eval(perms):
                return True
                break
    else:
        return cmd.perms

def perms_format(cmd):
    perms = cmd.perms.split('_')
    perms_str = ''
    for perm in perms:
        perms_str += '{} '.format(perm.title())

    return perms_str


async def print_all(message, client):
    msg = "**The following commands are available**:\n"
    for cmd in cmds:
        if get_perms(message, cmd) == True:
            args = get_args(cmd)
            msg += '\n`${0} {1}` - {2}'.format(cmd.name, args, cmd.desc)

    msg += '\n\n **You can use** `$help <command>` **for more information on each command** (Example: `$help echannel`)'

    await client.send_message(message.channel, msg)

async def print_spec(message, client, cmd):
    if cmd.args != 'null':
        args = get_args(cmd)
    else:
        args = ''

    msg = "**{0}**\n__Syntax__: `${0} {1}`\n__Description__: {2}".format(cmd.name, args, cmd.desc)

    if cmd.adv != 'null':
        msg += '\n__More__: {}'.format(cmd.adv)

    if cmd.example != 'null':
        msg += "\n__Example__: {}".format(cmd.example)

    if type(cmd.perms) != bool:
        perms = perms_format(cmd)
        msg += "\n__Perms Needed__: {}".format(perms)


    await client.send_message(message.channel, msg)

async def print_help(message, client):
    while True:
        await client.send_typing(message.channel)
        parse = message.content.split()
        try:
            spec = parse[1]
        except IndexError:
            await print_all(message, client)
            break

        if any(spec == o.name for o in cmds):
            cmd = get_cmd(spec)
        else:
            await client.send_message(message.channel, 'Command not found.')
            break

        await print_spec(message, client, cmd)
        break
