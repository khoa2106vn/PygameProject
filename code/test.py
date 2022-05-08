import pygame
from pygame.sprite import Sprite, Group

class Entity(Sprite):
    def __init__(self, image, position, anchor="topleft"):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        setattr(self.rect, anchor, position)
        self.position = pygame.Vector2(self.rect.center)

    def move_vector(self, vector):
        self.position += vector
        self.rect.center = self.position

class Dash:
    def __init__(self, velocity, run_time):
        self.vector = pygame.Vector2()
        self.velocity = velocity
        self.run_time = run_time
        self.is_dashing = False
        self.timer = -1

    def can_dash(self):
        return not self.is_dashing and self.timer == -1

    def end(self):
        self.is_dashing = False
        self.timer = -1

    def start(self, vector):
        if self.can_dash():
            self.timer = self.run_time
            self.is_dashing = True
            self.vector = vector

    def update(self, delta):
        if self.is_dashing:
            self.timer -= delta
            if self.timer <= 0:
                self.end()

class Player:
    def __init__(self, position):
        image = pygame.Surface((20, 20), pygame.SRCALPHA)
        image.fill(pygame.Color("dodgerblue"))
        self.entity = Entity(image, position, "center")
        self.dash = Dash(3, 0.3)
        self.velocity = 80
        self.facing = pygame.Vector2(0, -1)

    def draw(self, surface):
        surface.blit(self.entity.image, self.entity.rect)

    def start_dash(self):
        self.dash.start(self.facing)

    def update(self, delta):
        if not self.dash.is_dashing:
            keystate = pygame.key.get_pressed()
            direction = pygame.Vector2()
            if keystate[pygame.K_UP] or keystate[pygame.K_w]:
                direction.y -= 1

            if keystate[pygame.K_DOWN] or keystate[pygame.K_s]:
                direction.y += 1

            if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
                direction.x -= 1

            if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
                direction.x += 1

            if direction != pygame.Vector2():
                direction.normalize_ip()
                movement = direction * self.velocity * delta
                self.entity.move_vector(movement)
                self.facing = direction
        else:
            movement = self.dash.vector * self.velocity * delta
            self.entity.move_vector(movement * self.dash.velocity)
            self.dash.update(delta)

def main():
    pygame.display.set_caption("Dashing")
    surface = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    rect = surface.get_rect()
    running = True
    delta = 0
    fps = 60

    player = Player(rect.center)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.start_dash()
            elif event.type == pygame.QUIT:
                running = False

        surface.fill(pygame.Color("black"))
        player.draw(surface)
        player.update(delta)
        pygame.display.flip()
        delta = clock.tick(fps) * 0.001

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()