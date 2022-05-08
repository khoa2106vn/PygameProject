import pygame
from Timer import Timer
from debug import debug
from magic import MagicPlayer
from particles import AnimationPlayer

from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from upgrade import Upgrade
from Spark import *

class Level:
    def __init__(self):
        #get display surface
        self.game_paused = False
        self.ui = UI()
        self.display_surface = pygame.display.get_surface()
        self.timer = Timer()

        #sprite group
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        #sprite setup
        self.layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../map/map_Grass.csv'),
            'object': import_csv_layout('../map/map_Objects.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }

        self.graphics = {
            'grass': import_folder('../graphics/Grass'),
            'objects': import_folder('../graphics/objects'),
        }
        self.create_map()

        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        #upgrade
        self.upgrade = Upgrade(self.player)

        #monster spawn
        self.difficulty = 1 
        self.monster_spawn_radius = 500
        self.monster_spawn_cd = 800 / self.difficulty
        self.monster_spawn_time = 0

        self.screen_shake = 0
        self.render_offset = [0, 0]

        self.player_attacked = 0

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        
        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None
    
    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            #spawn particles
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
            self.screen_shake = 30
            self.player_attacked = 10
           
    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])


    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,50)
                            for leaf in range(randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset, self.visible_sprites)
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def spawn_monster(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.monster_spawn_time >= self.monster_spawn_cd:
    
            x = randint(8,80) * TILESIZE
            y = randint(8,52) * TILESIZE

            enemy_vec = pygame.math.Vector2(x,y)
            player_vec = pygame.math.Vector2(self.player.rect.center)
            distance = (player_vec - enemy_vec).magnitude()
            if distance >= 2000:

                monsters = randint(389,392)
                if monsters == 390: monster_name = 'bamboo'
                elif monsters == 391: monster_name = 'spirit'
                # elif monsters == 392: monster_name = 'raccoon'
                else: monster_name = 'squid'
                if monster_name == 'raccoon':
                    x = randint(7,23) * TILESIZE
                    y = randint(7,12) * TILESIZE
                self.monster_spawn_time = pygame.time.get_ticks()
                Enemy(
                    monster_name, 
                    (x,y), 
                    [self.visible_sprites, self.attackable_sprites],
                    self.obstacle_sprites,
                    self.damage_player,
                    self.trigger_death_particles,
                    self.add_exp,
                    self.difficulty
                )

    def increase_difficulty(self, time):
        self.difficulty = float(time / 60)
        if self.difficulty < 1:
            self.difficulty = 1 

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_map(self):
        for style, layout in self.layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col !='-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites], 'invisible')
                        # if style == 'grass':
                        #     random_grass_image = choice(self.graphics['grass'])

                        #     Tile((x,y),[self.visible_sprites,self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_image)
                        #     pass
                        # if style == 'object':
                        #     surf = self.graphics['objects'][int(col)]
                        #     Tile((x,y),[self.visible_sprites,self.obstacle_sprites], 'object', surf)

                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    (x,y),
                                    [self.visible_sprites], 
                                    self.obstacle_sprites,
                                    self.create_attack, 
                                    self.destroy_attack,
                                    self.create_magic,
                                    )
                            # else:
                            #     if col == '390': monster_name = 'bamboo'
                            #     elif col == '391': monster_name = 'spirit'
                            #     elif col == '392': monster_name = 'raccoon'
                            #     else: monster_name = 'squid'
                            #     Enemy(
                            #         monster_name, 
                            #         (x,y), 
                            #         [self.visible_sprites, self.attackable_sprites],
                            #         self.obstacle_sprites,
                            #         self.damage_player,
                            #         self.trigger_death_particles,
                            #         self.add_exp
                            #     )


    def run(self):
        self.visible_sprites.custom_draw(self.player, self.render_offset, self.player_attacked)
        self.ui.display(self.player, self.difficulty)
        if self.game_paused:
            self.upgrade.display()
            if self.timer.running == True:
                self.timer.pause()
        else:
            #update and draw
            if not self.timer.running:
                self.timer.resume()
            self.timer.update()

            if self.screen_shake > 0:
                self.screen_shake -= 1

            if self.screen_shake:
                self.render_offset[0] = randint(0, 14) - 8
                self.render_offset[1] = randint(0, 14) - 8
            
            if self.screen_shake == 0:
                self.render_offset[0] = 0
                self.render_offset[1] = 0
            if self.player_attacked > 0:
                self.player_attacked -= 1

            self.player_attack_logic()
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.spawn_monster()
            self.increase_difficulty(self.timer.get()/1000)
            
    def add_exp(self, amount):
        self.player.exp += amount
    
    def toggle_menu(self):
        self.game_paused = not self.game_paused

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        #setup
        super().__init__()
        #get display surface
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #floor creation
        self.floor_sur = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_sur.get_rect(topleft = (0,0))
        self.sparks = []


    def custom_draw(self, player, render_offset, player_attacked):
        #get offset from player
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_sur, floor_offset_pos + render_offset)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            if hasattr(sprite, 'health'):
                # pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, offset_postion + [32,57], 20)
                mask = pygame.mask.from_surface(sprite.image).outline()
                mask = [(-x + offset_position[0] + 62, -y + offset_position[1] + 115) for x,y in mask]
                pygame.draw.polygon(self.display_surface, pygame.Color(0,0,0), mask)
            self.display_surface.blit(sprite.image, offset_position + render_offset)
            if player_attacked > 0 and hasattr(sprite, 'is_player'):
                self.sparks.append(Spark([randint(0,20) - 10 + offset_position[0] + 32, randint(0,20) - 10 + offset_position[1] + 32], math.radians(random.randint(0, 360)), random.randint(3, 7), (136, 8, 8), 3))
    
        

        for i, spark in sorted(enumerate(self.sparks), reverse=True):
                spark.move(1)
                spark.draw(self.display_surface)
                if not spark.alive:
                    self.sparks.pop(i)



    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for sprite in enemy_sprites:
            sprite.enemy_update(player)