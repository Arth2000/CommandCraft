import re
from math import pow, cos, sin, ceil, pi

from pymclevel import TAG_Int, TAG_Compound, TAG_String


# Regex format
sq = re.compile(r'\[\[-?.+?(, ?-?.+?)*\]\]')
ang = re.compile(r'<<-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}>>')
par = re.compile(r'\(\(-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}\)\)')
cur = re.compile(r'\{\{-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}\}\}')

# how to place the commands blocks
direction = 'x'

# The sections.
sections = dict()

# The code parts.
parts = dict()

PLACEMENT = {  # The placement position
               'x': ({'y': -1, 'z': 0}, {'y': 1, 'z': 0}, {'z': 1, 'y': 0}, {'z': -1, 'y': 0}),
               'z': ({'x': 1, 'y': 0}, {'x': -1, 'y': 0}, {'y': -1, 'x': 0}, {'y': 1, 'x': 0})
}

# All the operators
OPERATORS = ('=', '+=', '-=', '*=', '/=', '%=', '>', '<', '><')

# Operators we can use in normal scoreboard commands
BASE_OPERATORS = {'=': 'set', '+=': 'add', '-=': 'remove'}

SECOND_OPERATORS = ('*=', '/=', '%=')

# the numbers values added on the scoreboard IDidntDefineItYet
numbers = []

SPECIAL_SELECTORS = {
    'me': {'c': '1', 'r': '0'},
    '!a': {'type': '!Player'}
}

SELECTORS = {  # The selectors
               # Mobs:
               'bats': {'type': 'Bat'}, 'blazes': {'type': 'Blaze'}, 'cavespiders': {'type': 'CaveSpider'},
               'chickens': {'type': 'Chicken'}, 'cows': {'type': 'Cow'}, 'creepers': {'type': 'Creeper'},
               'enderdragons': {'type': 'enderdragon'}, 'endermans': {'type': 'Enderman'},
               'endermites': {'type': 'Endermite'},
               'ghasts': {'type': 'Ghast'}, 'giants': {'type': 'Giant'}, 'guardians': {'type': 'Gurdian'},
               'horses': {'type': 'EntityHorse'}, 'magmacubes': {'type': 'LavaSlime'},
               'mushroom': {'type': 'MushroomCow'},
               'ocelots': {'type': 'Ozelot'}, 'pigs': {'type': 'Pig'}, 'pigzombies': {'type': 'PigZombie'},
               'rabbits': {'type': 'Rabbit'}, 'sheeps': {'type': 'Sheep'}, 'silverfishs': {'type': 'Silverfish'},
               'skeletons': {'type': 'Skeleton'}, 'slimes': {'type': 'Slime'}, 'snowman': {'SnowMan'},
               'spiders': {'type': 'Spider'}, 'squids': {'type': 'Squid'}, 'villagers': {'type': 'Villager'},
               'irongolem': {'type': 'VillagerGolem'}, 'witches': {'type': 'Witch'},
               'wither': {'type': 'WitherBoss'},
               'wolves': {'type': 'Wolf'}, 'zombies': {'type': 'Zombie'},
               # Projectiles:
               'arrows': {'type': 'Arrow'}, 'snowballs': {'type': 'Snowball'}, 'fireballs': {'type': 'Fireball'},
               'smallfireball': {'type': 'SmallFireball'}, 'enderpearls': {'type': 'ThrownEnderpearl'},
               'xpbottle': {'type': 'ThrownExpBottle'}, 'potions': {'type': 'ThrownPotion'},
               'witherskulls': {'type': 'WitherSkull'},
               # Capturable
               'items': {'type': 'Item'}, 'xp': {'type': 'XPOrb'},
               # Vehicle
               'boats': {'type': 'Boat'}, 'minecarts': {'type': 'MinecartRideable'},
               'chests': {'type': 'MinecartChests'},
               'furnaces': {'type': 'MinecartFurnace'}, 'spawners': {'type': 'MinecartSpawner'},
               'minecarttnt': {'type': 'MinecartTNT'}, 'hoppers': {'type': 'MinecartHopper'},
               'commands': {'type': 'MinecartCommandBlock'},
               # Tile entities
               'tnts': {'type': 'PrimedTnt'}, 'sands': {'type': 'FallingSand'},
               # Other
               'armor': {'type': 'ArmorStand'}, 'crystals': {'type': 'EnderCrystal'},
               'endersignals': {'type': 'EyeOfEnderSignal'}, 'fireworks': {'type': 'FireworkRocketEntity'},
               'itemframes': {'type': 'ItemFrame'}, 'leashknots': {'type': 'LeashKnot'},
               'paintings': {'type': 'Painting'}
}

VECTORS = {'x': 'tp {} ~{} ~ ~', 'y': 'tp {} ~ ~{} ~', 'z': 'tp {} ~ ~ ~{}'}


class End(Exception):
    """
    Raise when the filter find an error and have to end
    """
    pass


class EndOfAnalyse(Exception):
    """
    Raise when I finish to analyse something
    """
    pass


class AnalyseError(Exception):
    """
    Raise when an error occur while the filter analyses a command
    """
    pass


class Section:
    """
    A section of command blocks.
    blocks(section): yield all the commands with the position of the command block (x, y, z, command)
    self.name: name of the section
    self.width: the width of the section
    self.length: the length of the section
    self.commands: the commands
    self.base_pos: where the section begins
    self.trigger: a command that fill an area with blocks to activate/deactivate the section
    """

    def __init__(self, base_pos, commands, name):
        if len(commands) > 19998:
            raise End('Too much command in section ' + name + '. (total commands > 19998)')
        print len(commands)

        self.base_pos = base_pos
        self.commands = commands
        self._name = name
        self.width = (len(self.commands) + 1) / 200 + 1 if len(self.commands) > 398 else 1
        self.length = int(ceil((len(self.commands) + 2) / 4.0)) if self.width == 1 else \
            int(ceil((len(self.commands) + 2) / (2.0 * self.width)))

        global direction
        if direction == 'x':
            self.trigger = '/fill {0} {1} {2} {3} {1} {4}'.format(
                self.base_pos[0], self.base_pos[1] + 1,
                self.base_pos[2] + 1, self.base_pos[0] + self.length,
                self.base_pos[2] + self.width - 1
            ) + ' minecraft:{}'

        else:
            self.trigger = '/fill {0} {1} {2} {3} {1} {4}'.format(
                self.base_pos[0] + 1, self.base_pos[1] + 1,
                self.base_pos[2], self.base_pos[0] + self.width - 1,
                self.base_pos[2] + self.length
            ) + ' minecraft:{}'

    @property
    def name(self):
        return self._name


class Function(object, Section):
    """
    The function section type
    """
    def __init__(self, base_pos, commands, name):
        Section.__init__(self, base_pos, commands, name)
        self.commands.insert(0, self.trigger.format('stone'))
        self.commands.insert(0, self.trigger.format('redstone_block'))
        self._act = [self.trigger.format('redstone_block')]

    @property
    def act(self):
        return self._act


class Loop(object, Section):
    """
    The loop section type
    """
    def __init__(self, base_pos, commands, name):
        Section.__init__(self, base_pos, commands, name)
        self.commands.insert(0, self.trigger.format('redstone_block'))
        self.commands.insert(0, self.trigger.format('stone'))

        global direction
        if direction == 'x':
            end = '/setblock {} {} {}'.format(self.base_pos[0] - 1, self.base_pos[1],
                                              self.base_pos[2]) + ' minecraft:{}'

        else:
            end = '/setblock {} {} {}'.format(self.base_pos[0], self.base_pos[1],
                                              self.base_pos[2] - 1) + ' minecraft:{}'

        self._stop = [end.format('redstone_block')]
        self._start = [end.format('stone'), self.trigger.format('redstone_block')]

    @property
    def stop(self):
        """
        Commands that stop the loop
        """
        return self._stop

    @property
    def start(self):
        """
        Commands that make the loop running
        """
        return self._start


if direction == 'x':
    def blocks(obj):
        """
        blocks(Section) -> yield x, y, z, command
        Yield a command with the position of the command block
        """
        if obj.width == 1:
            for i in range(obj.length):
                for k, p in ((j, PLACEMENT['x'][j]) for j in xrange(4)):
                    yield (obj.base_pos[0] + i, obj.base_pos[1] + p['y'], obj.base_pos[2] + p['z'],
                           obj.commands[i * 4 + k])

        else:
            for j in xrange(obj.width):
                for i in xrange(obj.length):
                    yield (obj.base_pos[0] + i, obj.base_pos[1], obj.base_pos[2] + j,
                           obj.commands[j * obj.d * 2 + i * 2])
                    yield (obj.base_pos[0] + i, obj.base_pos[1] + 2, obj.base_pos[2] + j,
                           obj.commands[j * obj.d * 2 + i * 2 + 1])

else:
    def blocks(obj):
        """
        blocks(Section) -> yield x, y, z, command
        Yield a command with the position of the command block
        """
        if obj.width == 1:
            for i in range(obj.length):
                for k, p in ((j, PLACEMENT['z'][j]) for j in xrange(4)):
                    yield (obj.base_pos[0] + p['x'], obj.base_pos[1] + p['y'], obj.base_pos[2] + i,
                           obj.commands[i * 4 + k])
        else:
            for i in xrange(obj.length):
                for j in xrange(obj.width):
                    yield (obj.base_pos[0] + i, obj.base_pos[1], obj.base_pos[2] + j,
                           obj.commands[i * obj.width * 2 + j * 2])
                    yield (obj.base_pos[0] + i, obj.base_pos[1] + 1, obj.base_pos[2] + j,
                           obj.commands[i * obj.width * 2 + j * 2 + 1])


def command_formatting(command):
    """
    command_formatting(command) -> list of formatted commands
    Custom patterns:
        1. Execute: <sel> [pos] => <command>
        2. Detect: <sel> [pos] -> <block> [data]: <command>
        3. Vector: <selector> <x|y|z> <objective> <min value> <max value> <step> <min velocity> <max velocity>
        4. Scoreboard: <sel> <operation> <value 1> [value 2] ...
        5. Sin/cos: <sin|cos> <source objective|rotation> <step> <multiplier> [dest objective]
    """
    result = []
    command = command.strip()
    try:
        # execute format:
        # <sel> [pos] => <command>
        r = re.match(
            r'^(?P<sel>\S+) (?P<pos>(~?(-?\d+(\.\d*)?|\(\(-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}\)\)|\{\{-?\d+(\.\d*)?(:-?'
            r'\d+(\.\d*)?){0,2}\}\}|<<-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}>>|\[\[-?\d+(\.\d*)?(, ?-?\d+(\.\d*)?)*\]\]) )'
            r'{3})?=> (?P<c>.+)$',
            command)

        if r:
            result = ['/execute {} {}{}'.format(
                selector(r.group('sel')),
                r.group('pos') or "~ ~ ~ ",
                c
            ).strip() for c in command_formatting(r.group('c'))]

            raise EndOfAnalyse

        # detect format:
        # <sel> [pos] -> <block> [data]: <command>
        r = re.match(
            r'^(?P<sel>\S+) (?P<pos>(~?(-?\d+(\.\d*)?|\(\(-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}\)\)|\{\{-?\d+(\.\d*)?(:-?'
            r'\d+(\.\d*)?){0,2}\}\}|<<-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}>>|\[\[-?\d+(\.\d*)?(, ?-?\d+(\.\d*)?)*\]\]) )'
            r'{3})?-> (?P<block>(minecraft:)?[\w_]+)(?P<data> (-?\d+?|\(\(-?\d+(:-?\d+){0,2}\)\)|\{\{-?\d+(:-?\d+){0,2}'
            r'\}\}|<<-?\d+(:-?\d+){0,2}>>|\[\[-?\d+(, ?-?\d+)*\]\]))?: (?P<c>.+)$',
            command)

        if r:
            result = [
                '/execute {} ~ ~ ~ detect {} {} {} {}'.format(
                    selector(r.group('sel')),
                    r.group('pos') or '~ ~ ~ ',
                    r.group('block'),
                    r.group('data') or '-1',
                    c
                ).strip()
                for c in command_formatting(r.group('c'))
            ]

            raise EndOfAnalyse

        # Scoreboard pattern
        if re.match(r'^\S+ \S+ ((=|-=|\+=|/=|\*=|%=|>|<|><) (\S+|\S+ \S+))+$', command):
            parts = command.split(' ')
            sel = selector(parts.pop())
            obj = parts.pop()

            for i in (i for i in xrange(len(parts)) if parts[i] in OPERATORS):
                if parts[i] in BASE_OPERATORS and is_number(parts[i + 1]):
                    result.append(
                        '/scoreboard players {} {} {} {} {}'.format(
                            BASE_OPERATORS[parts[i]],
                            sel,
                            obj,
                            parts[i + 1],
                            parts[i + 2] if len(parts) > i + 2 and re.match(r'^\{.*\}$', parts[i + 2]) else ''
                        ).strip()
                    )

                elif parts[i] in SECOND_OPERATORS and is_number(parts[i + 1]):
                    result.append(
                        '/scoreboard players operation {} {} {} _num_{} _numbers'.format(
                            sel,
                            obj,
                            parts[i],
                            parts[i + 1]
                        )
                    )

                    if not parts[i + 1] in numbers:
                        numbers.append(parts[i + 1])

                elif re.match('^this\.\S+$', parts[i + 1]):
                    result.append(
                        '/execute {} ~ ~ ~ /scoreboard players operation @e[r=0,c=1] {} {} @e[r=0,c=1] {}'.format(
                            sel,
                            obj,
                            parts[i],
                            parts[i + 1][5:]
                        )
                    )

                elif parts[i + 2] in OPERATORS if len(parts) > i + 2 else True:
                    result.append(
                        '/scoreboard players operation {0} {1} {2} {3} {2}'.format(
                            sel,
                            obj,
                            parts[i],
                            selector(parts[i + 1])
                        ).strip()
                    )

                else:
                    result.append(
                        '/scoreboard players operation {} {} {} {} {}'.format(
                            sel,
                            obj,
                            parts[i],
                            selector(parts[i + 1]),
                            parts[i + 2]
                        ).strip()
                    )
            raise EndOfAnalyse

        # Vector pattern:
        # vector <selector> <x|y|z> <objective> <min value> <max value> <step> <min velocity> <max velocity>
        r = re.match(
            r'^vector (?P<sel>\S+) (?P<direc>[x-z]) (?P<obj>\S+) (?P<min_val>-?\d+) (?P<max_val>-?\d+)( (?P<step>-?\d+)'
            r' )?:(?P<min_vel>-?\d+(\.\d*)) (?P<max_vel>-?\d+(\.\d*))$', command)

        if r:
            sel = selector(r.group('sel'), 'score_{}_min'.format(r.group('obj')), 'score_{}'.format(r.group('obj')))
            start = int(r.group('min_val'))
            stop = int(r.group('max_val'))
            if stop < start:
                raise AnalyseError("Invalid parameter: '{}' must be lower than '{}' in '{}'.".format(
                    start, stop, command))

            step = int(r.group('step')) or 1
            min_vel = float(r.group('min_vel'))
            max_vel = float(r.group('max_vel'))

            if step <= 0:
                raise AnalyseError("Invalid parameter: '{}' must be greater than 0 in '{}'.".format(step, command))

            elif step > stop - start:
                raise AnalyseError("Invalid parameter: '{}' must be lower than '{}' minus '{}' in '{}'.".format
                                   (step, stop, start, command))

            c = VECTORS[r.group('direc')]

            vel_step = (max_vel - min_vel) / ((stop - start) / step)
            result = [c.format(sel.format(m, m + step - 1), m * vel_step) for m in xrange(
                start, stop + 1, step)]

            raise EndOfAnalyse

        # Square Root pattern:
        # sqrt <sel> <obj> <min val> <max val> [dest obj]
        r = re.match(r'^sqrt (?P<sel>\S+) (?P<obj>\S+) (?P<min_val>-?\d+) (?P<max_val>-?\d+)( (?P<dest_obj>\S+))?$',
                     command)
        if r:
            obj = r.group('obj')
            sel = selector(r.group('sel'), 'score_{}_min'.format(obj), 'score_{}'.format(obj))
            obj = r.group('dest_obj') or obj
            result = ['scoreboard players set {} {} {}'.format(
                sel.format(int(ceil(pow(value + 0.5, 2))), int(ceil(pow(value - 0.5, 2)))),
                obj, value)
                for value in xrange(int(r.group('min_val')), int('max_val'))
            ]
            raise EndOfAnalyse

        # Sin/cos pattern
        # <sin|cos> <source objective|rotation> <step> <multiplier> [dest objective]
        r = re.match(r'^(?P<op>(sin|cos)) (?P<sel>\S+) (?P<obj>\S+) (?P<step>\d+) (?P<mult>\d+)( (?P<dest_obj>\S+))?$',
                     command)

        if r:
            obj = r.group('sel')
            start = 0
            stop = 361
            fix = 0
            if obj in ('rx', 'ry'):
                sel = selector(r.group('sel'), obj + 'm', obj)
                if obj == 'rx':
                    start = -90
                    stop = 90

            elif obj in ('frx', 'fry'):
                sel = selector(r.group('sel'), obj[1:] + 'm', obj[1:])
                if obj == 'frx':
                    start = -90
                    stop = 91

                fix = 90

            dest = r.group('dest_obj') or obj
            step = int(r.group('step'))
            mult = int(r.group('mult'))
            result = [
                '/scoreboard players set {} {} {}'.format(
                    sel.format(i, i + step - 1),
                    dest,
                    int(round(sin(((i + fix) * 2 + step - 1) * pi / 360.) * mult))
                )
                for i in xrange(start, stop, step)
            ] if r.group('op') == 'sin' else [
                'scoreboard players set {} {} {}'.format(
                    sel.format(i, i + step - 1),
                    dest,
                    int(round(cos(((i + fix) * 2 + step - 1) * pi / 360.) * mult))
                )
                for i in xrange(start, stop, step)
            ]

            raise EndOfAnalyse

        r = re.match(r'^((?P<func>\$\S+)|(?P<loop>&\S+) (?P<act>(start|stop)))$', command)
        if r:
            func = r.group('func')
            if func:
                result = sections[func].act
                raise EndOfAnalyse

            act = r.group('act')
            if act == 'start':
                result = sections[r.group('loop')].start

            else:
                result = sections[r.group('loop')].stop

            raise EndOfAnalyse

    except EndOfAnalyse:
        return angle_generator(curly_generator(parenthesis_generator(square_generator(result))))

    except (IndexError, ZeroDivisionError, TypeError, ValueError):
        print "Invalid command {}. Command ignored.".format(command)
        return None

    except AnalyseError as e:
        print "{}. Command ignored.".format(e.message)
        return None


def angle_generator(commands):
    """
    angle_generator(commands) -> list of formatted commands
    Generate the angle generators:
        Angle generators (pattern: <<min[:max[:step]]>>) where every generator generate his value independently of the
         other.
    """
    if not commands or type(commands) != 'list':
        return commands

    try:
        global ang
        result = []
        for c in commands:
            if not ang.search(c):
                result.append(c)
                continue

            split = ang.split(c)
            rest_command = [split[i] for i in xrange(0, len(split), 4)]
            rest_command[0] = [rest_command[0]]
            for gen in ang.finditer(c):
                s = gen.group(0)[2:-2].split(':')
                t = []
                for v in (int(v) if re.match(r'^(-?\d+\.0?|-?\d+)$', str(v)) else v for v in frange(
                        float(s[0]),
                        float(s[1]) if len(s) >= 2 else None,
                        float(s[2]) if len(s) == 3 else 1)):

                    for c_p in rest_command[0]:
                        t.append(c_p + str(v) + rest_command[1])

                rest_command[0] = t
                rest_command.pop(1)

            result.extend(rest_command[0])

        return result

    except (TypeError, ValueError, ZeroDivisionError):
        print 'Error into an angle generator.'
        return commands


def curly_generator(commands):
    """
    curly_generator(commands) -> list of formatted commands
    Generate all the curly generators.
        Curly generators (pattern: {{min[:max[:step]]}}) generate all values at the same time for every generators.
    """

    if not commands or type(commands) != 'list':
        return commands

    try:
        result = []
        global cur
        for c in commands:
            if not cur.search(c):
                result.append(c)
                continue

            split = cur.split(c)
            rest_command = [split[i] for i in xrange(0, len(split), 4)]
            values = []
            for gen in cur.finditer(c):
                s = gen.group(0)[2:-2].split(':')

                values.append([int(v) if re.match(r'^(-?\d+\.0?|-?\d+)$', str(v)) else v for v in frange(
                    float(s[0]),
                    float(s[1]) if len(s) >= 2 else None,
                    float(s[2]) if len(s) == 3 else 1
                )])

            pps = len(rest_command)
            vals = zip(*values)
            for v in vals:
                r = ''
                for i in xrange(pps):
                    r += str(rest_command[i]) + str(v[i] if i < pps - 1 else '')

                result.append(r)

        return result

    except (TypeError, ValueError, ZeroDivisionError):
        print 'Error into a curly generator.'
        return commands


def parenthesis_generator(commands):
    """
    parenthesis_generator(commands) -> list of formated commands
    Generate every parenthesis generators in commands
    """
    # TODO: Finish it.

    if not commands or type(commands) != 'list':
        return commands

    try:
        result = []
        global par
        for c in commands:
            if not par.search(c):
                result.append(c)
                continue

            split = par.split(c)
            rest_command = [split[i] for i in xrange(0, len(split), 4)]
            rest_command[0] = [rest_command[0]]
            values = []
            ind = 0
            for gen in par.finditer(c):
                s = gen.group(0)[2:-2].split(':')
                t = []
                if len(s) >= 2:
                    ind += 1
                    values.append([int(v) if re.match(r'^(-?\d+\.0?|-?\d+)$', str(v)) else v for v in frange(
                        float(s[0]),
                        float(s[1]),
                        float(s[2]) if len(s) == 3 else 1
                    )])
                    for c_p in rest_command[0]:
                        t.append(c_p + '{' + str(ind) + '}' + rest_command[1])

                else:
                    for c_p in rest_command[0]:
                        t.append(c_p + s[0] + rest_command[1])

                rest_command[0] = t
                rest_command.pop(1)

            for vs in values:
                for val in vs:
                    for i in xrange(len(rest_command[0])):
                        rest_command[0][i] = rest_command[0][i].format(val)

            result.extend(rest_command[0])

        return result

    except (TypeError, ValueError, ZeroDivisionError):
        print 'Error into a parenthesis generator.'
        return commands


def square_generator(commands):
    """
    square_generator(commands) -> list of formatted commands
    Generate the square generators.
        [[<value 1>[, value 2[, ...]]]]
    """
    if not commands or type(commands) != 'list':
        return commands

    result = []
    global sq
    for c in commands:
        if not sq.search(c):
            result.append(c)
            continue

        split = sq.split(c)
        rest_command = [split[i] for i in xrange(0, len(split), 2)]
        rest_command[0] = [rest_command[0]]
        for gen in sq.finditer(c):
            t = []
            for v in re.split(r', ?', gen.group(0)[2:-2]):
                for c_p in rest_command[0]:
                    t.append(c_p + str(v) + rest_command[1])

            rest_command[0] = t
            rest_command.pop(1)

        result.extend(rest_command[0])

    return result


def selector(selec, *args, **kwargs):
    """
    selector(selec [, *args [, **kwargs]]) -> formatted selector
    Check if the selector 'selec' is correct or not.
    args parameters are added without specified values (for a .format() on the string)
    kwargs parameters are directly added in the selector
    """
    if selec[0] != '@':
        return selec

    params = []
    sel = selec.split('[')[0][1:]
    sel_l = sel.lower()

    if sel_l in SELECTORS:
        for k, v in SELECTORS[sel_l].items():
            params.append('{}={}'.format(k, v))

        sel = 'e'

    elif sel_l in SPECIAL_SELECTORS:
        for k, v in SPECIAL_SELECTORS[sel_l].items():
            params.append('{}={}'.format(k, v))

        sel = 'e'

    elif sel_l[0] == '!' and sel_l[1:] in SELECTORS:
        for k, v in SELECTORS[sel_l[1:]].items():
            params.append('{}=!{}'.format(k, v))

        sel = 'e'

    elif sel not in ('a', 'r', 'p', 'e'):
        params.append("name={}".format(sel))
        sel = 'e'

    r = re.match(r'^@\S+?\[(?P<args>\S*?)\]$', selec)
    if r:
        opt = r.group('args')
        if not opt:
            return '@{}{}'.format(
                sel,
                '[{}]'.format(
                    ','.join(params) + (',' if args else '') +
                    ','.join(arg + '={}' for arg in args) + (',' if kwargs else '') +
                    ','.join(k + '=' + v for k, v in kwargs.items())
                ) if params or args or kwargs else None
            )

        for param in opt.split(','):
            r = re.match(r'^(\S+)==(\d+)$', param)
            if r:
                params.append('score_{}_min={}'.format(r.group(1), r.group(2)))
                params.append('score_{}={}'.format(r.group(1), r.group(2)))
                continue

            r = re.match(
                r'^((?P<max>-?\d+)>=(?P<obj>\S+)>=(?P<min>-?\d+)|(?P<min_>-?\d+)<=(?P<obj_>\S+)<=(?P<max_>-?\d+))$',
                param)
            if r:
                d = r.groupdict()
                params.append('score_{}_min={}'.format(
                    d['obj'] if d['obj'] else d['obj_'],
                    d['min'] if d['min'] else d['min_']
                ))
                params.append('score_{}={}'.format(
                    d['obj'] if d['obj'] else d['obj_'],
                    d['max'] if d['max'] else d['max_']
                ))
                continue

            r = re.match(r'^((?P<obj>\S+)>=(?P<value>-?\d+)|(?P<value_>-?\d+)<=(?P<obj_>\S+))$', param)
            if r:
                d = r.groupdict()
                params.append('score_{}_min={}'.format(
                    d['obj'] if d['obj'] else d['obj_'],
                    d['value'] if d['value'] else d['value_']
                ))
                continue

            r = re.match(r'^((?P<value>-?\d+)>=(?P<obj>\S+)|(?P<obj_>\S+)<=(?P<value_>-?\d+))$', param)
            if r:
                d = r.groupdict()
                params.append('score_{}={}'.format(
                    d['obj'] if d['obj'] else d['obj_'],
                    d['value'] if d['value'] else d['value_']
                ))
                continue

            r = re.match(r'^(\S+?)=\S+$', param)
            if r:
                if re.match(r'^\S+?=\{\d*\}$', param):  # To prevent problems with *args
                    print("You can not use {} with or without number inside of the brackets in a selector. Parameter " +
                          param + " in selector " + selec + " ignored.")
                    continue

                elif r.group(1) in args:
                    continue

                params.append(param)

            else:
                print "Error into the parameter {} in the selector {}. Parameter ignored.".format(param, selec)

    if params or args or kwargs:
        p = ','.join(params) + (',' if args else '') + ','.join(arg + '={}' for arg in args) + (',' if kwargs else '') + \
            ','.join(k + '=' + str(v) for k, v in kwargs.items())

        return '@' + sel + '[' + (p[:-1] if p[-1] == ',' else p) + ']'

    return '@' + sel


def is_number(string):
    """
    is_number(string) -> bool
    Check if the string match one of the number generator format
    """
    return True if re.match(
        r'^(-?\d+(\.\d*)?|\{\{-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}\}\}|<<-?\d+(\.\d*)?(:-?\d+(\.\d*)?){0,2}>>|\(\(-?\d+'
        r'(\.\d*)?(:-?\d+(\.\d*)?){0,2}\)\)|\[\[-?\d+(\.\d*)?(, ?-?\d+(\.\d*)?)*\]\])$',
        string) else False


def frange(mini, maxi=None, step=1):
    """
    frange(min [, max [, step]]) -> yield min += step while min > max
    Same as xrange but also for floating numbers.
    """
    if maxi is None:
        maxi = mini
        mini = 0

    while mini < maxi:
        yield mini
        mini += step

# TODO: code analyser


def parts_finder(text):
    """
    Define the dict sections.
    """
    global parts
    p = re.split(r'^#', text)
    for i in xrange(len(p)):
        lines = p[i].splitlines()
        if re.match(r'^code [xz]$', lines[0]):
            global direction
            l = lines[0].split(' ')
            direction = l[1]
            parts[l[0]] = lines[1:]

        else:
            parts[lines[0]] = lines[1:]
            if lines[0] == "code":
                global direction
                direction = 'x'

    if "code" not in parts:
        raise End


def add_command_blocks():
    """
    Add the command blocks to the level.
    """
    global lvl
    for sec in sections.itervalues():
        for x, y, z, c in blocks(sec):
            chunk = lvl.getChunk(x / 16, z / 16)
            tile = lvl.tileEntityAt(x, y, z)
            if tile is not None:
                chunk.TileEntities.remove(tile)

            control = TAG_Compound()
            control["Command"] = TAG_String(c)
            control["id"] = TAG_String(u'Control')
            control["SuccessCount"] = TAG_Int(0)
            control["x"] = TAG_Int(x)
            control["y"] = TAG_Int(y)
            control["z"] = TAG_Int(z)
            chunk.TileEntities.append(control)
            chunk.dirty = True
            lvl.setBlockAt(x, y, z, 137)
            lvl.setBlockDataAt(x, y, z, 0)
            chunk.dirty = True


def add_objective(name, criteria, display=None):
    """
    add_objective(name, criteria[, display])
    Add the objective with the given properties.
    """
    global scoreboard_dat
    obj = TAG_Compound()
    obj['CriteriaName'] = TAG_String(criteria)
    obj['DisplayName'] = TAG_String(display or name)
    obj['Name'] = TAG_String(name)
    obj['RenderType'] = TAG_String("integer")
    scoreboard_dat["data"]["Objectives"].append(obj)


lvl = None
max_height = 0
scoreboard_dat = None

displayName = "CommandCraft V1.8.4 R0.1"

inputs = (
    ("Maximum Height", (255, 1, 255)),
    ('Code Path', ('string', 'value='))
)


def perform(level, box, options):
    lvl = level
    max_height = options["Maximum Height"]
    try:
        with open(options["Code Path"], "r") as cd:
            parts_finder(cd.read())

        scoreboard_dat = lvl.init_scoreboard
    except End:
        pass