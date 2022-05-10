import math
import pygame
from settings import *
from random import randint

class Gachapon:
    def __init__(self, player):

        #general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.trigger = True

        #item creation
        self.height = 128
        self.width = 128
        self.rollable_items = ['beaf', 'honey', 'sushi', 'tea_leaf']
        self.attribute_nr = len(self.rollable_items)
        self.create_items()

        #selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True
        self.move_fx = pygame.mixer.Sound('../audio/Menu1.wav')
        self.move_fx.set_volume(0.3)

    def input(self):
        if self.trigger:
            self.ran_item = randint(1, 400)
            self.trigger = False
        if self.ran_item > 0:
            self.ran_item -= 1
            if self.can_move:
                if self.selection_index < self.attribute_nr - 1:
                    self.selection_index += 1
                    self.move_fx.play()
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()
                else:
                    self.selection_index = 0
                    self.move_fx.play()
                    self.can_move = False
                    self.selection_time = pygame.time.get_ticks()


    def create_items(self):
        self.item_list = []

        for item, index in enumerate(range(len(self.rollable_items))):
            #horizontal position
            full_width = self.display_surface.get_size()[0]
            increment = full_width // len(self.rollable_items)
            left = (item * increment) + (increment - self.width) // 2

            #vertical position
            top = self.display_surface.get_size()[1] * 0.1

            #create object
            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 150:
                self.can_move = True

    def display(self):
        self.input()
        self.selection_cooldown()
        
        for index, item in enumerate(self.item_list):
            #get attributes
            name = self.rollable_items[index]
            item.display(self.display_surface, self.selection_index, name)

class Item:
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font
        self.up = pygame.mixer.Sound('../audio/Gold1.wav')
        self.up.set_volume(0.3)
        self.c_up = pygame.mixer.Sound('../audio/Menu12.wav')
        self.c_up.set_volume(0.3)


    def display_names(self, surface, name, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        #title
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0,20))

        #draw
        surface.blit(title_surf, title_rect)
    

    def display(self, surface, selection_num, name):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_names(surface, name, self.index == selection_num)