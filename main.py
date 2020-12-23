import pygame
import sys
from pygame.locals import *
from PIL import Image
import numpy
import random
import math
from copy import copy
from pygame.locals import *

SCREEN_W = 600
SCREEN_H = 800

directions = [[-1, 0], [+1, 0], [0, -1], [0, +1], [-1, -1], [+1, +1], [+1, -1], [-1, +1]]
INFLUENCE_RANGE = 5
TRIBE_SPLIT_LIMIT = 80
NEW_TRIBE_SIZE = 100000
BASE_GROWTH_RATE = 0.0001
LACK_OF_WATER_DEATH_MOD = 20
BASE_DEATH_RATE = BASE_GROWTH_RATE / 15
                    
STARTING_TECH = {'moving_on_water': 0,
                 'water_preservation': 0}
STARTING_INVENTIONS = {'water_preservation': False,
                      }


STARTING_POP = {}
EXTRACTING_PRODUCT = {}
TEMPLATE_INFO = {}
FOOD_PRODUCING = set()
FOOD_PRODUCING_DETAILED = {}
BASIC_DEATH_RATE = {}
ZERO_OCCUPATION_DICT = {}
OCCUPATIONS = set()
OCC_ID = {}
UNUSED_OCC_ID = 0
EMPTY_RESOURCES = dict()
RES_TO_STOCK = dict()
MATERIALS = set()
FOOD = set()
GOODS = set()
CRAFT = dict()
NEED_TOOLS = dict()

morae = [i + j for i in ['s', 'k', 't', 'm', 'n', 'h', 'r', ''] for j in ['i', 'e', 'u', 'a', 'o']]

def generate_name():
    n = random.randint(2, 4)
    tmp = ''
    for i in range(n):
        tmp += random.choice(morae)
    return tmp

def add_material(m):
    MATERIALS.add(m['name'])
    
def add_goods(g):
    GOODS.add(g['name'])
    
def add_resource(r):
    RES_TO_STOCK[r['name']] = r['product']
    EMPTY_RESOURCES[r['name']] = 0

def add_food(f):
    FOOD.add(f['name'])
    
def stock_list_sum(a, in_place = False):
    global FOOD
    global MATERIALS
    global GOODS
    if in_place:
        stock = a[0]
    else:
        stock = dict()
    stock['food'] = dict()
    for i in FOOD:
        stock['food'][i] = 0
        for s in a:
            stock['food'][i] += s['food'][i]
    for i in GOODS:
        stock[i] = dict()   
        for j in ['0']:
            stock[i][j] = 0
            for s in a:
                stock[i][j] += s[i][j]
    stock['materials'] = dict()
    for i in MATERIALS:
        stock['materials'][i] = 0
        for s in a:
            stock['materials'][i] += s['materials'][i]
    stock['water'] = 0
    for s in a:
        stock['water'] += s['water']
    return stock

def stock_sum(a, b, in_place = False):
    if in_place:
        return stock_list_sum([a, b], True)
    return stock_list_sum([a, b])

def get_empty_stock():
    return stock_list_sum([])
    
def add_to_stock(s, a, name, mat = None):
    if name in FOOD:
        s['food'][name] += math.floor(a)
    if name in MATERIALS:
        s['materials'][name] += math.floor(a)
    if name in GOODS:
        s[name][mat] += math.floor(a)

def stock_transfer(a, b):
    stock_sum(b, a, True)

def get_total_amount_stock(s, a):
    if a == 'water':
        return s[a]
    t = 0
    for i in s[a]:
        t += s[a][i]
    return t

def add_pop_occupation(p):
    global STARTING_POP
    global STARTING_TECH
    global EXTRACTING_PRODUCT
    global TEMPLATE_INFO
    global FOOD_PRODUCING
    global FOOD_PRODUCING_DETAILED
    global BASIC_DEATH_RATE
    global ZERO_OCCUPATION_DICT
    global OCC_ID
    global UNUSED_OCC_ID
    global OCCUPATIONS
    OCCUPATIONS.add(p['name'])
    if 'is_main_pop' in p:
        STARTING_POP[p['name']] = NEW_TRIBE_SIZE
    else:
        STARTING_POP[p['name']] = 0
    if 'starting_tech' in p:
        STARTING_TECH[p['name']] = p['starting_tech']
    else:
        STARTING_TECH[p['name']] = 0
    if 'extracting_product' in p:
        EXTRACTING_PRODUCT[p['name']] = p['extracting_product'].copy()
        TEMPLATE_INFO[p['name']] = dict()
        for (res, amount) in p['extracting_product']:
            for (tmp, amount) in RES_TO_STOCK[res]:
                TEMPLATE_INFO[p['name']][tmp] = 0
    if 'production' in p:
        INPUT[p['name']] = p['input']
        OUTPUT[p['name']] = p['output']
    if 'food_producing' in p:
        FOOD_PRODUCING.add(p['name'])
        FOOD_PRODUCING_DETAILED[p['name']] = p['food_producing']
    if 'craft' in p:
        CRAFT[p['name']] = True
    if 'need_tools' in p:
        NEED_TOOLS[p['name']] = p['need_tools']
    BASIC_DEATH_RATE[p['name']] = BASE_DEATH_RATE
    ZERO_OCCUPATION_DICT[p['name']] = 0
    OCC_ID[p['name']] = UNUSED_OCC_ID
    UNUSED_OCC_ID += 1

add_material({'name': 'wood'})
add_material({'name': 'stone'})
add_material({'name': 'bone'})
add_material({'name': 'small_bone'})

add_food({'name': 'meat'})
add_food({'name': 'fish'})
add_food({'name': 'plants'})

add_goods({'name': 'weapons'})
add_goods({'name': 'small_tools'})
add_goods({'name': 'tools'})

add_resource({'name': 'game', 'product': [('meat', 1), ('raw_hides', 1), ('bone', 1)]})
add_resource({'name': 'wild_plants', 'product': [('plants', 1)]})
add_resource({'name': 'plants', 'product': [('plants', 1)]})
add_resource({'name': 'river_fish', 'product': [('fish', 1), ('small_bone', 1)]})
add_resource({'name': 'forest', 'product': [('wood', 10)]})
    
add_pop_occupation({'name': 'gathering',
                    'is_main_pop': 1,
                    'extracting_product': [('wild_plants', 1)],
                    'food_producing': 'plants',
                    'starting_tech': 3})
add_pop_occupation({'name': 'hunt',
                    'extracting_product': [('game', 1)],
                    'food_producing': 'meat',
                    'starting_tech': 4})
add_pop_occupation({'name': 'agrari',
                    'extracting_product': [('plants', 1)],
                    'food_producing': 'plants'})
add_pop_occupation({'name': 'river_fish',
                    'extracting_product': [('river_fish', 1)],
                    'food_producing': 'fish'})
add_pop_occupation({'name': 'craft', 
                    'craft': 1})
add_pop_occupation({'name': 'woodcutter',
                    'extracting_product': [('forest', 1)],
                    'need_tools': True})


STARTING_STOCK = get_empty_stock()

BASE_RES = EMPTY_RESOURCES.copy()
BASE_RES['game'] = 12
BASE_RES['river_fish'] = 0
BASE_RES['plants'] = 0
BASE_RES['wild_plants'] = 80

BASE_RES_RIVER = EMPTY_RESOURCES.copy()
BASE_RES_RIVER['game'] = 12
BASE_RES_RIVER['river_fish'] = 20
BASE_RES_RIVER['plants'] = 80
BASE_RES_RIVER['wild_plants'] = 40

BASE_RES_GROWTH = EMPTY_RESOURCES.copy()
BASE_RES_GROWTH['game'] = 12
BASE_RES_GROWTH['wild_plants'] = 20

BASE_RES_GROWTH_RIVER = EMPTY_RESOURCES.copy()
BASE_RES_GROWTH_RIVER['game'] = 12
BASE_RES_GROWTH_RIVER['river_fish'] = 10

BASIC_COLOR = (250, 250, 250)

ORGA_THREE = 80
# ORGA_GAIN_BASE_PROBABILITY = 0.001
# SEDENTARY_BASE_PROBABILITY = 0.00001
ORGA_GAIN_BASE_PROBABILITY = 0.1
SEDENTARY_BASE_PROBABILITY = 0.1
MAX_ORGA = 0

TOTAL_POPULATION = ZERO_OCCUPATION_DICT.copy()
TOTAL_POPULATION_GRAPH = [(ZERO_OCCUPATION_DICT.copy(), False) for i in range(400)]

DRAW_GRAPH = False
DRAW_RIVERS = False
DRAW_MAP = False
PAUSE = False
MAP_MODE = 1
EPS = 0.0000001

def norm(v):
    return numpy.sqrt(v[0] ** 2 + v[1] ** 2)

def dist(a, b):
    return numpy.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

class TribeUnion:
    def __init__(self, world, tribes, color):
        pass


class Army:
    def __init__(self, world, x, y, size):
        self.world = world
        self.x = x
        self.y = y
        self.size = size

class Tribe:
    def __init__(self, world, centres, color, overlord = None):
        self.is_influence_agent = True
        self.world = world
        self.centres = set(copy(centres))
        self.main_centre = centres[0]
        self.bands = set(copy(centres))
        self._color = color
        self.id = world.get_new_id()
        self.name = generate_name()
        self.del_flag = False
        self.overlord = overlord
        self.soldiers = Army(self.world, self.main_centre.x, self.main_centre.y, 0)
    
    @property
    def total_size(self):
        return sum([i.size for i in self.bands])
        
    def get_soldiers(self):
        return self.main_centre.stock['weapons']['0']
        return self.soldiers.size
        
    def update(self):
        for i in self.bands:
            d = INFLUENCE_RANGE + 1
            for j in self.centres:
                d = min(d, dist(i, j))
            if d > INFLUENCE_RANGE:
                self.world.new_event({'type': 'band_exit_tribe', 'band_id': i.id, 'tribe_id': self.id})
            else:
                stock_transfer(i.stock, self.main_centre.stock)
        if self.main_centre.stock['weapons']['0'] >= 1:
            if self.main_centre.get_man():
                self.soldiers.size += 1
                self.main_centre.stock['weapons'] -= 1       
    
    def join(self, x):
        self.bands.add(x)

    def exit(self, x):
        self.bands.discard(x)
        self.centres.discard(x)
        if len(self.centres) == 0 and not self.del_flag:
            self.world.new_event({'type': 'del_tribe', 'id': self.id})
            self.del_flag = True
        
    @property
    def color(self):
        return self._color

class Band:
    def __init__(self, world, x, y, pop, tech, inventions, tribe):
        self.is_influence_agent = False
        self.world = world
        self.id = world.get_new_id()
        self.x = x 
        self.y = y 
        self.world.occupied_land[x][y] = True
        self.world.band_from_coord[x][y] = self
        self.tribe = tribe
        self.pop = copy(pop)
        self.tech = copy(tech)
        self.inventions = copy(inventions)
        self.death_rate = copy(BASIC_DEATH_RATE)
        self.growth_progress = copy(ZERO_OCCUPATION_DICT)
        self.death_progress = copy(ZERO_OCCUPATION_DICT)
        self.stock = get_empty_stock()
        self.organization = 1
        self.sedentary = False
        self.push = 0
        self.flag_enough_food = True
        self.productivity_mult = 1
        
        self.del_flag = False
        self.last_pos = (0, 0)
        
    @property
    def size(self):
        return sum(self.pop[i] for i in self.pop)
        
    @property
    def productive_force(self):
        s = 0
        for i in OCCUPATIONS:
            if i not in CRAFT:
                continue
            if CRAFT[i]:
                s += self.pop[i]
        return s
        
    @property
    def food_stock(self):
        s = 0
        for i in FOOD:
            s += self.stock['food'][i]
        return s
        
    @property
    def water_stock(self):
        return self.stock['water']
        
    def get_man(self):
        mp = 'gathering'
        for i in OCCUPATIONS:
            if self.pop[i] > self.pop[mp]:
                mp = i
        if self.pop[mp] > 0:
            self.pop[mp] -= 1
            return True
        return False
        
    def substract_water(self, x):
        self.stock['water'] = max(0, self.stock['water'] - x)
        
    def substruct_food(self, x):
        s = self.food_stock
        for i in FOOD:
            t = self.stock['food'][i]
            self.stock['food'][i] = max(0, t - x * t // s)
    
    def update(self):
        if self.size <= 0 and not self.del_flag:
            self.world.new_event({'type': 'del_band', 'id': self.id})
            return
        
        if self.del_flag:
            return
            
        nutrient_value, water, info, info_max = self.gather_update()
        # print('!!!')
        # print(self.world.res_limit[self.x][self.y])
        # print(self.world.res[self.x][self.y])
        # print(self.tech)
        # print(info)
        # print(info_max)
        self.production_update()
        self.flag_update(nutrient_value, water)
        self.migrate_update()
        alive = self.size_update()
        if not alive:
            return
        self.tech_update()
        self.update_pop_occupation(info, info_max)
        self.orga_update()
        self.split_update()
        self.stock_preservation_update()
    
    def flag_update(self, nv, water):
        if nv >= self.size:
            self.flag_enough_food = True
        else:
            self.flag_enough_food = False
        if water >= self.size:
            self.flag_enough_water = True
        else:
            self.flag_enough_water = False
        self.nutrient_per_being = nv / self.size
        self.productivity_mult = 1 + get_total_amount_stock(self.stock, 'tools') / self.size
        
        
    def size_update(self):
        s = self.size
        for i in self.pop:
            self.death_progress[i] += self.death_rate[i] * self.pop[i]
            food_for_this_pop = math.trunc(min(self.food_stock * self.pop[i] // s + 1, self.pop[i]))
            water_for_this_pop = math.trunc(min(self.water_stock * self.pop[i] // s + 1, self.pop[i]))
            self.growth_progress[i] += BASE_GROWTH_RATE * (min(food_for_this_pop, water_for_this_pop) - self.pop[i] / 2) * 2
            if water_for_this_pop < self.pop[i]:
                self.death_progress[i] += self.pop[i] / LACK_OF_WATER_DEATH_MOD
            self.change_food(-food_for_this_pop)
            self.change_water(-water_for_this_pop)
            t = math.floor(self.growth_progress[i])
            d = math.floor(self.death_progress[i])
            self.pop[i] = max(0, self.pop[i] + (t - d))
            self.growth_progress[i] -= t
            self.death_progress[i] -= d
        if self.size <= 0:
            self.world.new_event({'type': 'del_band', 'id': self.id})
            return False
        return True
    
    def change_water(self, x):
        self.stock['water'] += x
        if self.stock['water'] < 0:
            self.stock['water'] = 0
        
    def change_food(self, n):
        s = self.food_stock
        if s == 0 or n == 0:
            return
        for f in FOOD:
            x = self.stock['food'][f]
            self.stock['food'][f] += math.floor(x / s * n)
            if self.stock['food'][f] < 0:
                self.stock['food'][f] = 0
        
    def production_update(self):
        s = math.floor(self.productive_force * self.productivity_mult)
        size = self.size
        print(self.stock['materials']['wood'], self.stock['materials']['stone'], s) 
        if get_total_amount_stock(self.stock, 'tools') <= (self.size) // 2:
            amount = min(self.stock['materials']['wood'], self.stock['materials']['stone'], s)
            self.stock['materials']['wood'] -= amount
            self.stock['materials']['stone'] -= amount
            self.stock['tools']['0'] += amount
        else:
            amount = min(self.stock['materials']['wood'], self.stock['materials']['stone'], s)
            self.stock['materials']['wood'] -= amount
            self.stock['materials']['stone'] -= amount
            self.stock['weapons']['0'] += amount
                
    
    def gather_update(self):
        a, info, info_max = self.world.extract(self.x, self.y, self.pop, self.tech, self.productivity_mult)
        self.stock = stock_sum(self.stock, a)
        water = self.world.extract_water(self.x, self.y, self.size)
        self.stock['water'] += water
        self.stock['materials']['stone'] += math.floor(self.size * self.productivity_mult)
        if info['woodcutter']['wood'] != 0:
            print('!!!!')
        return sum(a['food'][i] for i in FOOD), water, info, info_max
    
    def orga_update(self):
        d = random.random()
        if d < ORGA_GAIN_BASE_PROBABILITY * self.size / self.organization:
            self.organization += 1
        d = random.random()
        if d < ORGA_GAIN_BASE_PROBABILITY * 2 and self.sedentary:
            self.organization += 1
        if self.organization > 60 and not self.sedentary:
            self.organization = 60
        if self.organization >= ORGA_THREE and self.tribe is None:
            self.world.new_event({'type': 'new_tribe', 'centres': [self.id]})
    
    def split_update(self):
        if self.organization < ORGA_THREE:
            if self.size > TRIBE_SPLIT_LIMIT * (1 + self.organization / 100):
                possible_destination = []
                for dv in directions:
                    if self.world.valid_for_life(self.x + dv[0], self.y + dv[1]) and self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]] is None:
                        possible_destination.append([self.x + dv[0], self.y + dv[1]])
                if len(possible_destination) > 0:
                    d = random.randint(0, len(possible_destination) - 1)
                    x = possible_destination[d][0]
                    y = possible_destination[d][1]
                    self.world.occupied_land[x][y] = True
                    new_pop = copy(ZERO_OCCUPATION_DICT)
                    for i in new_pop:
                        new_pop[i] = math.floor(self.pop[i] * 0.5 / self.organization)
                        self.pop[i] = self.pop[i] - new_pop[i]
                    self.world.new_event({'type': 'new_band', 'x': x, 'y': y, 'pop': new_pop, 'tech': self.tech, 'inventions': self.inventions, 'tribe': self.tribe})
                for dv in directions:
                    if self.world.valid_for_life(self.x + dv[0], self.y + dv[1]) and self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]] is None:
                        tmp = self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]]
                        if tmp != -1 and not tmp is None:
                            tmp.push += self.push + 1
        
    def migrate_update(self):
        if (not (self.flag_enough_food and self.flag_enough_water) and self.sedentary is False) or self.push > self.size // 10:
            possible_destination = []
            for dv in directions:
                if self.last_pos[0] == dv[0] and self.last_pos[1] == dv[1]:
                    continue
                if self.world.valid_for_life(self.x + dv[0], self.y + dv[1]) and self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]] is None:
                    possible_destination.append([self.x + dv[0], self.y + dv[1]])
            if len(possible_destination) > 0:
                d = random.randint(0, len(possible_destination) - 1)
                self.last_pos = (-possible_destination[d][0], -possible_destination[d][1])
                self.world.occupied_land[self.x][self.y] = False
                self.world.band_from_coord[self.x][self.y] = None
                self.x = possible_destination[d][0]
                self.y = possible_destination[d][1]
                self.world.occupied_land[self.x][self.y] = True
                self.world.band_from_coord[self.x][self.y] = self
            else:
                self.last_pos = (0, 0)
                for dv in directions:
                    if self.world.valid_for_life(self.x + dv[0], self.y + dv[1]) and self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]] is None:
                        tmp = self.world.band_from_coord[self.x + dv[0]][self.y + dv[1]]
                        if tmp != -1 and not tmp is None:
                            tmp.push += self.push + 2
    
    def tech_update(self):
        if self.flag_enough_food and self.flag_enough_water and self.sedentary is False:
            d = random.random()
            if d < SEDENTARY_BASE_PROBABILITY:
                self.sedentary = True
            if self.tech['agrari'] >= 1 and d < 0.05:
                self.sedentary = True
        for i in self.tech:
            if self.sedentary:
                d = random.random()
                if d < 0.5 and self.tech['agrari'] <= 8:
                    self.tech['agrari'] += 0.5
                elif self.tech['agrari'] > 5:
                    d = random.random()
                    if d < 0.001:
                        self.tech['agrari'] += 0.001
            if i == 'water_preservation' and self.inventions['water_preservation']:
                d = random.random()
                if d < 0.1 and self.tech['water_preservation'] < 1 / 3:
                    self.tech['water_preservation'] += 0.01
            if i == 'river_fish' and self.world.near_river[self.x][self.y]:
                if self.tech['moving_on_water'] < 1:
                    d = random.random()
                    if d < 0.05 and self.tech['river_fish'] < 4:
                        self.tech['river_fish'] += 0.2
                else:
                    d = random.random()
                    if d < 0.1 and self.tech['river_fish'] < 6:
                        self.tech['river_fish'] += 0.5
            else:
                d = random.random()
                if d < 0.001:
                    self.tech[i] += 0.001
        if not self.inventions['water_preservation']:
            d = random.random()
            if d < math.log(self.water_stock // 100 + 1):
                self.inventions['water_preservation'] = True
    
    def update_pop_occupation(self, info, info_max):
        if self.nutrient_per_being > 2:
            mi = -1
            for i in FOOD_PRODUCING:
                food_tag = FOOD_PRODUCING_DETAILED[i]
                if (mi == -1 or info[mi][mi_food_tag] > info[i][food_tag]) and self.pop[i] != 0:
                    mi = i 
                    mi_food_tag = food_tag
            if mi != -1 and self.pop[mi] > 0:
                d = random.random()
                if d < 0.5:
                    self.pop['woodcutter'] += 1
                else:
                    self.pop['craft'] += 1
                self.pop[mi] -= 1
        else:
            if self.pop['craft'] > self.pop['woodcutter']:
                mi = 'craft'
            else:
                mi = 'woodcutter'
            ma = -1
            for i in FOOD_PRODUCING:
                food_tag = FOOD_PRODUCING_DETAILED[i]
                if ma == -1 or info[ma][ma_food_tag] < info[i][food_tag] and info[i][food_tag] > info_max[i][food_tag] - EPS:
                    ma = i 
                    ma_food_tag = food_tag
            if mi != -1 and info[ma][ma_food_tag] > 0 and self.pop[mi] > 0:
                self.pop[mi] -= 1
                self.pop[ma] += 1
            
        mi = -1
        for i in FOOD_PRODUCING:
            food_tag = FOOD_PRODUCING_DETAILED[i]
            if (mi == -1 or info[mi][mi_food_tag] > info[i][food_tag]) and self.pop[i] != 0:
                mi = i 
                mi_food_tag = food_tag
        ma = -1
        for i in FOOD_PRODUCING:
            food_tag = FOOD_PRODUCING_DETAILED[i]
            if ma == -1 or info[ma][ma_food_tag] < info[i][food_tag] and info[i][food_tag] > info_max[i][food_tag] - EPS:
                ma = i 
                ma_food_tag = food_tag
        if mi != -1 and info[ma][ma_food_tag] > 0:
            self.pop[mi] -= 1
            self.pop[ma] += 1
    
    def stock_preservation_update(self):
        for i in FOOD:
            self.stock['food'][i] = math.floor(self.stock['food'][i] * 0.9)
        self.stock['water'] = self.stock['water'] * self.tech['water_preservation']
        for i in MATERIALS:
            self.stock['materials'][i] = math.floor(self.stock['materials'][i] * 0.9)
    
    @property
    def color(self):
        if self.tribe is None:
            t = min(self.organization / ORGA_THREE, 1)
            t = t / 2 + 1/2
            return tuple(map(math.floor, (BASIC_COLOR[0] * t, BASIC_COLOR[1] * t, BASIC_COLOR[2] * t)))
        return self.tribe.color

class World:
    def __init__(self, map, rivers, fer, forest):
        self.map = map
        self.rivers = rivers
        self.agents = dict()
        self.tribes = dict()
        self.fer_map = fer
        self.forest_map = forest
        self.color_id = 0
        self.tribe_color_id = 0
        self.color = dict()
        self.events = []
        self.last_id = 0
        self.res = [[copy(EMPTY_RESOURCES) for i in range(1000)] for j in range(1000)]
        self.res_limit = [[copy(EMPTY_RESOURCES) for i in range(1000)] for j in range(1000)]
        self.fertility = [[0 for i in range(1000)] for j in range(1000)]
        self.occupied_land = [[False for i in range(1000)] for j in range(1000)]
        self.water = [[False for i in range(1000)] for j in range(1000)]
        self.near_river = [[False for i in range(1000)] for j in range(1000)]
        self.band_from_coord = [[None for i in range(1000)] for j in range(1000)]
        self.pixel_needs_update = set()
        self.year = 0
        self.season = 0
        self.day = 0
        self.hour = 0
        for x in range(500):
            for y in range(500):
                self.init_pixel(x, y)
    
    def init_pixel(self, x, y):
        if self.valid_for_life(x, y):
            self.res[x][y] = BASE_RES.copy()
            self.res_limit[x][y] = BASE_RES.copy()
        for d in directions:
            if self.inside_map(x + d[0], y + d[1]):
                if 0 < sum_rgb(self.rivers[x + d[0]][y + d[1]]) < 540:
                    self.water[x][y] = True
                    self.near_river[x][y] = True
                    for i in EMPTY_RESOURCES:
                        self.res[x][y][i] += BASE_RES_RIVER[i]
                        self.res_limit[x][y][i] += BASE_RES_RIVER[i]
                    # self.fertility[x][y] = BASE_FERTILITY_NEAR_RIVERS
                    
        if sum_rgb(self.rivers[x][y]) > 600:
            self.water[x][y] = True
            self.near_river[x][y] = True
            for i in EMPTY_RESOURCES:
                self.res[x][y][i] += BASE_RES_RIVER[i]
                self.res_limit[x][y][i] += BASE_RES_RIVER[i]
            # self.fertility[x][y] = BASE_FERTILITY_NEAR_RIVERS
        self.fertility[x][y] = self.fer_map[x][y][3] // 2
        self.res[x][y]['forest'] = self.forest_map[x][y][3]
        self.res_limit[x][y]['forest'] = self.forest_map[x][y][3]
    
    def add_agent(self, obj):
        self.agents[obj.id] = obj
        
    def add_tribe(self, obj):
        self.tribes[obj.id] = obj
        return self.tribes[obj.id]
        
    def get_new_id(self):
        self.last_id += 1
        return self.last_id
    
    def get_free_union_color(self):
        self.color_id += 7
        return hsv_to_rgb_int((self.color_id) * 12 % 360, 0.8, 0.9)
        
    def get_free_tribe_color(self):
        self.tribe_color_id += 7
        return hsv_to_rgb_int((self.tribe_color_id) * 12 % 360, 0.8, 0.5)
        
    def new_event(self, event):
        self.events.append(event)
        if event['type'] == 'new_band':
            self.band_from_coord[event['x']][event['y']] = -1
    
    def update_influence(self):
        visited = set()
        in_process = set()
        dist = dict()
        color = dict()
        for i1 in self.tribes:
            i = self.tribes[i1]
            if i.is_influence_agent:
                for j in i.centres:
                    v = (j.x, j.y)
                    dist[v] = 0
                    in_process.add(v)
                    color[v] = i.id
                # j = i.centres[0]
                # v = (j.x, j.y)
                # dist[v] = 0
                # in_process.add(v)
                # color[v] = i.id
        while len(in_process) > 0:
            curr = None
            for i in dist:
                if (curr == None or dist[curr] > dist[i]) and i in in_process:
                    curr = i
            visited.add(curr)
            in_process.discard(curr)
            for dv in directions:
                neig = (curr[0] + dv[0], curr[1] + dv[1])
                if dist[curr] + norm(dv) > INFLUENCE_RANGE or not self.valid_for_life(neig[0], neig[1]):
                    continue
                if neig in in_process:
                    if dist[neig] > dist[curr] + norm(dv):
                        dist[neig] = dist[curr] + norm(dv)
                        color[neig] = color[curr]
                else:
                    dist[neig] = dist[curr] + norm(dv)
                    color[neig] = color[curr]
                    in_process.add(neig)
        for i in color:
            if self.valid_for_life(i[0], i[1]) and not self.band_from_coord[i[0]][i[1]] is None and self.band_from_coord[i[0]][i[1]] != -1:
                if self.band_from_coord[i[0]][i[1]].tribe is None or self.band_from_coord[i[0]][i[1]].tribe.id != color[i]:
                    self.new_event({'type': 'join_tribe', 'band_id': self.band_from_coord[i[0]][i[1]].id, 'tribe_id': color[i]})
        return color
    
    def draw_bands(self, surface):
        if MAP_MODE == 0:
            for i in self.color:
                if self.color[i] in self.tribes:
                    surface[i[1]][i[0]] = self.tribes[self.color[i]].color
        if MAP_MODE == 1:
            for i in self.agents:
                if not self.agents[i].is_influence_agent:
                    agent = self.agents[i]
                    surface[agent.y][agent.x] = agent.color
    
    def draw(self):
        global TOTAL_POPULATION_GRAPH
        surface = pygame.PixelArray(screen)
        self.draw_bands(surface)
        if DRAW_GRAPH:
            for i in range(len(TOTAL_POPULATION_GRAPH)):
                if TOTAL_POPULATION_GRAPH[i][1]:
                    for j in range(300):
                        surface[i][SCREEN_H - 1 - j] = (100, 100, 100)
                z = 0
                s = 1 + sum(TOTAL_POPULATION_GRAPH[i][0][b] for b in TOTAL_POPULATION_GRAPH[i][0])
                if s == 1:
                    continue
                lo = math.log(s)
                for j in TOTAL_POPULATION_GRAPH[i][0]:
                    color = hsv_to_rgb_int(OCC_ID[j] * 360 / 10, 1, 1)                
                    for k in range(math.floor(lo * TOTAL_POPULATION_GRAPH[i][0][j] / (s - 1) * 5)):
                        surface[i][max(SCREEN_H - 1 - z, 0)] = color
                        z += 1
        del surface
        
    def update(self):
        global MAX_ORGA
        global TOTAL_POPULATION
        global TOTAL_POPULATION_GRAPH
        TOTAL_POPULATION = ZERO_OCCUPATION_DICT.copy()
        for i in self.events:
            if i['type'] == 'new_band':
                band = Band(self, i['x'], i['y'], i['pop'], i['tech'], i['inventions'], i['tribe'])
                self.band_from_coord[i['x']][i['y']] = band
                self.add_agent(band)
            if i['type'] == 'del_band':
                if i['id'] in self.agents:
                    a = self.agents[i['id']]
                    if not a.tribe is None:
                        a.tribe.exit(a)
                    self.band_from_coord[a.x][a.y] = None
                    self.agents.pop(i['id'], None)
            if i['type'] == 'del_tribe':
                a = self.tribes[i['id']]
                for j in a.bands:
                    j.tribe = None
                self.tribes.pop(i['id'], None)
            if i['type'] == 'stop_update_pixel':
                self.pixel_needs_update.discard((i['x'], i['y']))
            if i['type'] == 'new_tribe':
                tribe = self.add_tribe(Tribe(self, [self.agents[j] for j in i['centres']], self.get_free_tribe_color()))
                for j in i['centres']:
                    self.agents[j].tribe = tribe
            if i['type'] == 'join_tribe':
                if i['band_id'] in self.agents and i['tribe_id'] in self.tribes:
                    if not self.agents[i['band_id']].tribe is None:
                        self.agents[i['band_id']].tribe.exit(self.agents[i['band_id']])
                    self.agents[i['band_id']].tribe = self.tribes[i['tribe_id']]
                    self.tribes[i['tribe_id']].join(self.agents[i['band_id']])
            if i['type'] == 'band_exit_tribe':
                if i['band_id'] in self.agents:
                    self.agents[i['band_id']].tribe = None
                if i['tribe_id'] in self.tribes and i['band_id'] in self.agents:
                    self.tribes[i['tribe_id']].exit(self.agents[i['band_id']])
        self.events = []
        for i in self.pixel_needs_update:
            self.update_pixel(i[0], i[1])
        MAX_ORGA = 0
        # tmp = set()
        for i in self.agents:
            # tmp.add((self.agents[i].x, self.agents[i].y))
            if not self.agents[i].is_influence_agent:
                d = random.random()
                if d < 0.1:
                    if not self.agents[i].is_influence_agent and self.agents[i].size < 3:
                        self.agents[i].del_flag = True
                        self.new_event({'type': 'del_band', 'id': self.agents[i].id})
                self.agents[i].update()
                if self.agents[i].organization > MAX_ORGA:
                    MAX_ORGA = self.agents[i].organization
                for j in self.agents[i].pop:
                    TOTAL_POPULATION[j] += self.agents[i].pop[j]
        for i in self.tribes:
            self.tribes[i].update()
        # print(len(tmp))
        self.hour = self.hour + 1
        if self.hour >= 10:
            self.color = self.update_influence()
            self.hour = 0
            self.day += 1
            TOTAL_POPULATION_GRAPH = TOTAL_POPULATION_GRAPH[1:] + [(TOTAL_POPULATION, False)]
        if self.day >= 30:
            self.day = 0
            self.season += 1
            TOTAL_POPULATION_GRAPH[-1] = (TOTAL_POPULATION, True)
        if self.season >= 4:
            self.season = 0
            self.year += 1
    
    def update_pixel(self, x, y):
        need_update = False
        for i in EMPTY_RESOURCES:
            limit = self.res_limit[x][y][i]
            fer = self.fertility[x][y]
            if i == 'wild_plants':
                if self.season != 0:
                    self.res[x][y][i] += fer // 6
                else:
                    self.res[x][y][i] += fer // 3
                if self.res[x][y][i] > limit:
                    self.res[x][y][i] = limit
                if self.res[x][y][i] < limit and fer != 0:
                    need_update = True
            if i == 'plants':
                if self.season == 0:
                    self.res[x][y][i] += fer
                if self.res[x][y][i] > limit:
                    self.res[x][y][i] = limit
                if fer != 0 and self.res[x][y][i] < limit:
                    need_update = True
            if i == 'river_fish' or i == 'game':
                self.res[x][y][i] = min(limit, self.res[x][y][i] + limit // 10) 
                if self.res[x][y][i] < limit:
                    need_update = True
            if i == 'forest':
                self.res[x][y][i] = min(limit, self.res[x][y][i] + limit // 20) 
                if (self.res[x][y][i] < limit) and (self.res[x][y][i] + limit // 20 != 0):
                    need_update = True
        if not need_update:
            self.new_event({'type': 'stop_update_pixel', 'x': x, 'y': y})
            
    def valid_for_life(self, x, y):
        if not self.inside_map(x, y):
            return False
        if sum_rgb(self.rivers[x][y]) > 600:
            return True
        if sum_rgb(self.rivers[x][y]) != 0:
            return False
        r, g, b, a = self.map[x][y]
        if b > 240:
            return False
        if r + g > 400:
            return False
        return True
    
    def inside_map(self, x, y):
        if x < 0 or x > 800:
            return False
        if y < 0 or y > 800:
            return False
        return True
    
    def extract(self, x, y, pop, tech, mult):
        self.pixel_needs_update.add((x, y))
        result = 0
        info = TEMPLATE_INFO.copy()
        info_max = TEMPLATE_INFO.copy()
        stock = get_empty_stock()
        for i in OCCUPATIONS:
            if i not in EXTRACTING_PRODUCT:
                continue
            for (res, res_amount) in EXTRACTING_PRODUCT[i]:
                max_amount_per_worker = res_amount * tech[i] * self.get_season_extraction_mult(res) * mult
                res_amount_extracted = math.floor(pop[i] ** (19/20) * max_amount_per_worker)
                if res_amount_extracted > self.res[x][y][res]:
                    res_amount_extracted = self.res[x][y][res]
                # if pop[i] != 0 and  res_amount_extracted / pop[i] < 1.5 - EPS and self.fertility[x][y] != 0:
                    # print(i)
                    # print(res_amount, tech[i], self.get_season_extraction_mult(res))
                    # print(max_amount_per_worker)
                    # print(pop[i])
                    # print(res_amount_extracted, '|', self.res[x][y][res])
                    # print(res_amount_extracted / pop[i])
                self.res[x][y][res] -= res_amount_extracted
                for (name, amount) in RES_TO_STOCK[res]:
                    a = res_amount_extracted * amount
                    add_to_stock(stock, a, name)
                    if pop[i] != 0:
                        info[i][name] = a / pop[i]
                    if math.floor(max_amount_per_worker) > self.res[x][y][res]:
                        info_max[i][name] += self.res[x][y][res] * amount
                    else:
                        info_max[i][name] += max_amount_per_worker * amount
        return stock, info, info_max
        
    def get_season_extraction_mult(self, typ):
        if ((self.season != 0) or (self.season != 1)) and (typ == 'plants' or typ == 'wild_plants'):
            return 0.5
        return 1
        
    def extract_water(self, x, y, size):
        if self.water[x][y]:
            return size * 2
        else:
            return 0
        

def hsv_to_rgb(H, S, V):
    C = V * S
    Hs = H / 60
    X = C * (1 - abs(Hs % 2 - 1))
    if 0 <= Hs <= 1:
        r1, g1, b1 = C, X, 0
    elif 1 < Hs <= 2:
        r1, g1, b1 = X, C, 0
    elif 2 < Hs <= 3:
        r1, g1, b1 = 0, C, X
    elif 3 < Hs <= 4:
        r1, g1, b1 = 0, X, C
    elif 4 < Hs <= 5:
        r1, g1, b1 = X, 0, C
    elif 5 < Hs <= 6:
        r1, g1, b1 = C, 0, X
    m = V - C
    return (255 * (r1 + m), 255 * (g1 + m), 255 * (b1 + m))

def hsv_to_rgb_int(H, S, V):
    return tuple(map(math.floor, hsv_to_rgb(H, S, V)))

def sum_rgb(a):
    return a[0] + a[1] + a[2]

file_name = 'map2.png'

mi = Image.open(file_name)
ma = numpy.array(mi).tolist()

riv_raw = Image.open('rivers.png')
riv = numpy.array(riv_raw).tolist()

fer_raw = Image.open('fertility.png')
fer = numpy.array(fer_raw).tolist()

forest_raw = Image.open('forest.png')
forest = numpy.array(forest_raw).tolist()

world = World(ma, riv, fer, forest)

pygame.init()
pygame.display.set_caption('just another unfinished project. again')
pygame.font.init()
myfont = pygame.font.SysFont("Arial", 14)
band1 = Band(world, 58, 250, STARTING_POP, STARTING_TECH, STARTING_INVENTIONS, None)
band1.organization = 1

world.add_agent(band1)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), 0, 32)
screen.fill((255, 255, 255))

background = pygame.image.load(file_name)
rivers = pygame.image.load('rivers.png')
screen.blit(background, (0, 0))
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_g:
                DRAW_GRAPH = not DRAW_GRAPH
            if event.key == K_m:
                DRAW_MAP = not DRAW_MAP
            if event.key == K_LEFT:
                MAP_MODE = (MAP_MODE + 1) % 2
            if event.key == K_r:
                DRAW_RIVERS = not DRAW_RIVERS
            if event.key == K_p:
                PAUSE = not PAUSE
    if not PAUSE:
        world.update()
    screen.fill((0, 0, 0))
    if DRAW_MAP:
        screen.blit(background, (0, 0))
    if DRAW_RIVERS:
        screen.blit(rivers, (0, 0))
    world.draw()
    text_org = myfont.render('MAX_ORGA ' + str(MAX_ORGA), False, (100, 100, 100))
    text_population = myfont.render('POPULA ' + str(sum(TOTAL_POPULATION[i] for i in OCCUPATIONS)), False, (100, 100, 100))
    if len(world.agents) != 0:
        medium_size = sum(TOTAL_POPULATION[i] for i in OCCUPATIONS) // len(world.agents)
    else:
        medium_size = -1
    text_medium_size = myfont.render('MED_POPU ' + str(medium_size), False, (100, 100, 100))
    text_year = myfont.render('year ' + str(world.year), False, (100, 100, 100))
    text_season = myfont.render('season ' + str(world.season), False, (100, 100, 100))
    text_day = myfont.render('day ' + str(world.day), False, (100, 100, 100))
    text_hour = myfont.render('hour ' + str(world.hour), False, (100, 100, 100))
    # text_tech = myfont.render(
                               # str(
                                 # ' '.join(
                                   # map(
                                     # lambda x: str(math.floor(x * 1000)),
                                     # (world.agents[1].tech[i] for i in world.agents[1].tech)
                                   # )
                                 # )
                               # ),
                               # False,
                               # (100, 100, 100)
                             # )
    screen.blit(text_org, (5, 0))
    screen.blit(text_population, (5, 20))
    screen.blit(text_medium_size, (5, 40))
    screen.blit(text_year, (5, 60))
    screen.blit(text_season, (5, 80))
    screen.blit(text_day, (5, 100))
    screen.blit(text_hour, (5, 120))
    z = 140
    for j in TOTAL_POPULATION_GRAPH[-1][0]:
        color = hsv_to_rgb_int(OCC_ID[j] * 360 / 10, 1, 1)
        prof_text = myfont.render(j + ' ' + str(TOTAL_POPULATION_GRAPH[-1][0][j]), False, color)
        screen.blit(prof_text, (5, z))
        z += 20
    t = []
    if MAP_MODE == 0 or MAP_MODE == 1:
        for i in world.tribes:
            tribe = world.tribes[i]
            t.append([tribe.color, tribe.total_size, tribe.main_centre.size, len(tribe.bands), tribe.name, tribe.overlord, tribe.get_soldiers()])
        t.sort(key = lambda x: -x[1])
        columns = [   5,           90,               180,                    270,              360,        450,            540]
        screen.blit(myfont.render('tribe_pop', False, (100, 100, 100)), (columns[0], z))
        screen.blit(myfont.render('centre_pop', False, (100, 100, 100)), (columns[1], z))
        screen.blit(myfont.render('bands_count', False, (100, 100, 100)), (columns[2], z))
        screen.blit(myfont.render('name', False, (100, 100, 100)), (columns[3], z))
        screen.blit(myfont.render('overlord', False, (100, 100, 100)), (columns[4], z))
        screen.blit(myfont.render('soldiers', False, (100, 100, 100)), (columns[5], z))
        z += 20
        for i in t:
            color = i[0]
            total_pop_text = myfont.render(str(i[1]), False, color)
            centre_pop_text = myfont.render(str(i[2]), False, color)
            amount_of_bands_text = myfont.render(str(i[3]), False, color)
            name_text = myfont.render(i[4], False, color)
            if i[5] != None:
                overlord_text = myfont.render(i[5].name, False, i[5].color)
            else:
                overlord_text = myfont.render('None', False, color)
            soldiers_text = myfont.render(str(i[6]), False, color)
            screen.blit(total_pop_text, (columns[0], z))
            screen.blit(centre_pop_text, (columns[1], z))
            screen.blit(amount_of_bands_text, (columns[2], z))
            screen.blit(name_text, (columns[3], z))
            screen.blit(overlord_text, (columns[4], z))
            screen.blit(soldiers_text, (columns[5], z))
            z += 20
    elif MAP_MODE == 2:
        pass
    fps = myfont.render(str(int(clock.get_fps())), True, (100, 100, 100))
    screen.blit(fps, (SCREEN_W - 59, 10))
    clock.tick()
    pygame.display.update()