import pytest
from commandcraft import Section, Loop, Function, End, blocks, is_number, selector, frange, angle_generator, \
    curly_generator, parenthesis_generator, square_generator, parts_finder


def section_ft(base_pos=(0, 60, 0), commands=None, name="default name"):
    if not commands:
        commands = ['/tellraw @a {text:"This is a test!"}', '/tellraw @a {text:"This is also a test!"}']
    return Section(base_pos, commands, name)


def function_ft(base_pos=(0, 60, 0), commands=None, name="default name"):
    if not commands:
        commands = ['/tellraw @a {text:"This is a test!"}', '/tellraw @a {text:"This is also a test!"}']
    return Function(base_pos, commands, name)


def loop_ft(base_pos=(0, 60, 0), commands=None, name="default name"):
    if not commands:
        commands = ['/tellraw @a {text:"This is a test!"}', '/tellraw @a {text:"This is also a test!"}']
    return Loop(base_pos, commands, name)


@pytest.fixture
def angle_commands():
    return ['<<3>>', '<<40:42>>', '<<40.1:42>>', '<<-3.1415:7:3.1415>>',
            '/tellraw @a {text:"This is test number #<<10>>!"}',
            '/say gen n1: #<<-3.14:3.15:3.14>>. gen n2: #<<0:43:21>>']


@pytest.fixture
def curly_commands():
    return ['{{3}}', '{{40:42}}', '{{40.1:42}}', '{{-3.1415:7:3.1415}}',
            '/tellraw @a {text:"This is test number #{{10}}!"}',
            '/say gen n1: #{{-3.14:3.15:3.14}}. gen n2: #{{0:43:21}}',
            '/say t n1: #{{0:3}}. n2: #{{1:3}}']


def test_section_creation():
    assert isinstance(section_ft(), Section)


def test_section_creation_exception():
    with pytest.raises(End):
        section_ft(commands=range(19999))


def test_section_width_equals_1():
    assert section_ft().width == 1


def test_section_witdth_equals_3():
    assert section_ft(commands=range(399)).width == 3


def test_section_width_greater_than_3():
    assert section_ft(commands=range(17980)).width == 90


def test_length_when_width_equals_1_number_1():
    assert section_ft(commands=range(300)).length == 76


def test_length_when_width_equals_1_number_2():
    assert section_ft(commands=range(398)).length == 100


def test_length_with_a_big_value():
    assert section_ft(commands=range(19000)).length == 99


def test_function_blocks():
    f = function_ft()
    result = ''
    for px, py, pz, co in blocks(f):
        result += '{}{}{}{}'.format(px, py, pz, co)

    assert result == '0590/fill 0 61 1 1 61 0 minecraft:redstone_block0610/fill 0 61 1 1 61 0 minecraft:stone0601/tellraw @a {text:"This is a test!"}060-1/tellraw @a {text:"This is also a test!"}'


def test_function_act():
    assert function_ft().act == ['/fill 0 61 1 1 61 0 minecraft:redstone_block']


def test_loop_blocks():
    result = ""
    l = loop_ft()
    for px, py, pz, co in blocks(l):
        result += '{}{}{}{}'.format(px, py, pz, co)

    assert result == '0590/fill 0 61 1 1 61 0 minecraft:stone0610/fill 0 61 1 1 61 0 minecraft:redstone_block0601/tellraw @a {text:"This is a test!"}060-1/tellraw @a {text:"This is also a test!"}'


def test_loop_start():
    assert loop_ft().start == ['/setblock -1 60 0 minecraft:stone', '/fill 0 61 1 1 61 0 minecraft:redstone_block']


def test_loop_stop():
    assert loop_ft().stop == ["/setblock -1 60 0 minecraft:redstone_block"]


def test_is_number_with_a_number():
    assert is_number('42')


def test_is_number_with_angle():
    assert is_number('<<1:23>>')


def test_is_number_with_curly():
    assert is_number('{{42:666}}')


def test_is_number_with_parenthesis():
    assert is_number('((42:666))')


def test_is_number_with_square():
    assert is_number('[[42, 666]]')


def test_is_number_with_float():
    assert is_number('666.666')


def test_is_number_with_angle_and_float():
    assert is_number('<<0.1:0.2:0.01>>')


def test_is_number_with_curly_and_floats():
    assert is_number('{{-0.0:666.666:42.03}}')


def test_is_number_with_parenthesis_and_floats():
    assert is_number('((-43.0:777.25637189:3.1415))')


def test_is_number_with_square_and_floats():
    assert is_number('[[42,0, 666, 77.97298103, 3.141592653]]')


def test_isnt_a_number_with_string():
    assert not is_number('A String')


def test_isnt_a_number_with_square():
    assert not is_number('[[42, 666, String]]')


def test_frange_only_min():
    j = 0
    for i in frange(42):
        assert i == j
        j += 1


def test_frange_wih_max():
    j = -666.666
    for i in frange(-666.666, 666.666):
        assert i == j
        j += 1


def test_frange_with_step():
    j = -666.666
    for i in frange(-666.666, 42, 3.141592):
        assert i == j
        j += 3.141592


def test_selector_name():
    assert selector('Arth2000') == 'Arth2000'


def test_selecor_without_params():
    assert selector('@a') == '@a'


def test_selector_without_params_with_type():
    assert selector('@items') == '@e[type=Item]'


def test_selector_without_params_with_negative_type_name():
    assert selector('@!cows') == '@e[type=!Cow]'


def test_selector_without_params_with_custom_selector():
    assert selector('@me') in ('@e[c=1,r=0]', '@e[r=0,c=1]')


def test_selector_without_params_with_name():
    assert selector('@Hero') == '@e[name=Hero]'


def test_selector_with_normal_params():
    assert selector('@e[name=Arth2000,type=Player]') == '@e[name=Arth2000,type=Player]'


def test_selector_with_equal_scoreboard():
    assert selector('@e[name=Arth2000,god==0]') == '@e[name=Arth2000,score_god_min=0,score_god=0]'


def test_selector_with_double_smaller_than_scoreboard():
    assert selector('@e[name=Arth2000,-1<=god<=0]') == '@e[name=Arth2000,score_god_min=-1,score_god=0]'


def test_selector_with_double_greater_than_scoreboard():
    assert selector('@e[name=Arth2000,0>=god>=-1]') == '@e[name=Arth2000,score_god_min=-1,score_god=0]'


def test_selector_with_smaller_than_scoreboard():
    assert selector('@e[name=Arth2000,god<=0]') == '@e[name=Arth2000,score_god=0]'


def test_selector_with_greater_than_scoreboard():
    assert selector('@e[name=Arth2000,god>=-1]') == '@e[name=Arth2000,score_god_min=-1]'


def test_selector_with_args():
    assert selector('@Arth2000', 'r', 'c') == '@e[name=Arth2000,r={},c={}]'


def test_selector_with_kwargs():
    assert selector('@Arth2000', 'type', r='1', c='-1') in ('@e[name=Arth2000,type={},r=1,c=-1]',
                                                            '@e[name=Arth2000,type={},c=-1,r=1]')


def test_selector_with_everything():
    assert selector('@!a[name=Arth2000,1>=god>=0,death<=7,t>=1]', 'c', r='1000') == \
           '@e[type=!Player,name=Arth2000,score_god_min=0,score_god=1,score_death=7,score_t_min=1,c={},r=1000]'


def test_angle_generator(angle_commands):
    assert angle_generator(*angle_commands) == ['0', '1', '2', '40', '41', '40.1', '41.1', '-3.1415', '0', '3.1415',
                                                '6.283', '/tellraw @a {text:"This is test number #0!"}',
                                                '/tellraw @a {text:"This is test number #1!"}',
                                                '/tellraw @a {text:"This is test number #2!"}',
                                                '/tellraw @a {text:"This is test number #3!"}',
                                                '/tellraw @a {text:"This is test number #4!"}',
                                                '/tellraw @a {text:"This is test number #5!"}',
                                                '/tellraw @a {text:"This is test number #6!"}',
                                                '/tellraw @a {text:"This is test number #7!"}',
                                                '/tellraw @a {text:"This is test number #8!"}',
                                                '/tellraw @a {text:"This is test number #9!"}',
                                                '/say gen n1: #-3.14. gen n2: #0',
                                                '/say gen n1: #0. gen n2: #0',
                                                '/say gen n1: #3.14. gen n2: #0',
                                                '/say gen n1: #-3.14. gen n2: #21',
                                                '/say gen n1: #0. gen n2: #21',
                                                '/say gen n1: #3.14. gen n2: #21',
                                                '/say gen n1: #-3.14. gen n2: #42',
                                                '/say gen n1: #0. gen n2: #42',
                                                '/say gen n1: #3.14. gen n2: #42']


def test_curly_generator(curly_commands):
    assert curly_generator(*curly_commands) == ['0', '1', '2', '40', '41', '40.1', '41.1', '-3.1415', '0', '3.1415',
                                                '6.283', '/tellraw @a {text:"This is test number #0!"}',
                                                '/tellraw @a {text:"This is test number #1!"}',
                                                '/tellraw @a {text:"This is test number #2!"}',
                                                '/tellraw @a {text:"This is test number #3!"}',
                                                '/tellraw @a {text:"This is test number #4!"}',
                                                '/tellraw @a {text:"This is test number #5!"}',
                                                '/tellraw @a {text:"This is test number #6!"}',
                                                '/tellraw @a {text:"This is test number #7!"}',
                                                '/tellraw @a {text:"This is test number #8!"}',
                                                '/tellraw @a {text:"This is test number #9!"}',
                                                '/say gen n1: #-3.14. gen n2: #0', '/say gen n1: #0. gen n2: #21',
                                                '/say gen n1: #3.14. gen n2: #42', '/say t n1: #0. n2: #1',
                                                '/say t n1: #1. n2: #2']


def test_parenthesis_generator_with_maxi():
    assert parenthesis_generator('((-3:3))') == ['-3', '-2', '-1', '0', '1', '2']


def test_parenthesis_generator_with_step():
    assert parenthesis_generator('((-3:3:1.5))') == ['-3', '-1.5', '0', '1.5']


def test_parenthesis_generator_with_index():
    assert parenthesis_generator('((-3:3:1.5)) ((0))') == ['-3 -3', '-1.5 -1.5', '0 0', '1.5 1.5']


def test_parenthesis_generator_with_multiple_indices():
    assert parenthesis_generator('((-3:3:1.5)) ((6:8)) ((0)) ((1))') == ['-3 6 -3 6', '-1.5 6 -1.5 6', '0 6 0 6',
                                                                         '1.5 6 1.5 6', '-3 7 -3 7', '-1.5 7 -1.5 7',
                                                                         '0 7 0 7', '1.5 7 1.5 7']


def test_parenthesis_generator_with_text():
    assert parenthesis_generator('/say Test number ((-3:3:1.5)). value: ((0))') == ['/say Test number -3. value: -3',
                                                                                    '/say Test number -1.5. value: -1.5',
                                                                                    '/say Test number 0. value: 0',
                                                                                    '/say Test number 1.5. value: 1.5']


def test_square_generator():
    assert square_generator('[[Something, 42, 3.141592, <<-3:3:1.5>>, something you may like]]') \
        == ['Something', '42', '3.141592', '<<-3:3:1.5>>', 'something you may like']


def test_parts_finder_exists():
    assert parts_finder is not None


def test_parts_finder_raise_end_exception_when_no_code_section():
    with pytest.raises(End):
        parts_finder("#")


def test_parts_finder_only_code():
    assert parts_finder("#code\nsay hi") == {"code": ["say hi"]}


def test_parts_finder_with_more_sections():
    assert parts_finder("#code\nsay hi\nsay hia\n#variables\n%a = b") == {"code": ["say hi", "say hia"],
                                                                          "variables": ["%a = b"]}