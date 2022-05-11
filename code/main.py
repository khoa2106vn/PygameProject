import pygame, sys
from settings import *
from level import Level


class Game:
    def __init__(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Nhom 1 - Survival Project')

        self.level = Level()

        #sound
        self.main_sound = pygame.mixer.Sound('../audio/main.wav')
        self.main_sound.set_volume(0.05)
        self.accept = pygame.mixer.Sound('../audio/Accept.wav')
        self.accept.set_volume(0.2)
        self.state = 'main_game'
        self.started = False
        self.main_sound.play(loops = -1)
        self.font = pygame.font.Font(UI_FONT, 50)
        self.screen_rect = self.screen.get_rect()
        self.restart_f = False

    def intro(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.accept.play()
                    self.started = True
                    self.state = 'main_game'
                    self.level.timer.started = True
    
    def state_manager(self):
        if self.state == 'intro':
            self.intro()
        if self.state == 'main_game':
            self.main_game()
        if self.state == 'restart':
            self.restart_f = True
            self.level = Level()
            self.state = 'main_game'
            self.level.timer.started = True
    
    def get_image(self, sheet, width, height):
        image = pygame.Surface((width, height)).convert_alpha()

        return image

    def main_game(self):
        self.screen.fill(WATER_COLOR)
        self.level.run()
        if not self.started:
            title_surf = self.font.render('press enter to start', False, (255,255,255))
            title_rect = title_surf.get_rect(center = (self.screen_rect.center[0], self.screen_rect.center[1] + 200))
            self.screen.blit(title_surf, title_rect)
        pygame.display.update()
        if not self.started:
            self.state = 'intro'
        if self.restart_f:
            self.restart_f = False
            self.accept.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.level.toggle_menu()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.level.toggle_inventory()
        if self.level.player.health < 0 and self.level.player.restart_pressed:
            self.state = 'restart'

    def run(self):
        while True:
            self.state_manager()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()