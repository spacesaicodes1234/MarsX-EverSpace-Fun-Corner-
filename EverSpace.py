
import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EverSpace v1.01")

# Load enemies
RED_SPACE_SHIP = pygame.image.load(os.path.join("pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("pixel_ship_blue_small.png"))

# Player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join( "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("background.png")), (WIDTH, HEIGHT))

#HEALING

HEAL = pygame.image.load(os.path.join("med.png"))
HEART = pygame.image.load(os.path.join("heart.png"))

class Laser:
    
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 25
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=250):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            
            self.cool_down_counter = 1

class Heal(Ship):

    def __init__(self, x, y, health=10000000):
        super().__init__(x, y, health)
        self.ship_img = HEAL
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += vel

class Heart(Ship):

    def __init__(self, x, y, health=10000000):
        super().__init__(x, y, health)
        self.ship_img = HEART
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 90
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Berlin Sans FB", 50)
    lost_font = pygame.font.SysFont("Berlin Sans FB", 60)
    loss_font = pygame.font.SysFont("Berlin Sans FB", 80)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    Medkit = []
    num = 1
    med_vel = 1

    hearts = []
    num1 =1
    
    heart_beat = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (240,0,255))
        level_label = main_font.render(f"Round: {level}", 1, (240,0,255))
      

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for med in Medkit:
            med.draw(WIN)

        for heart in hearts:
            heart.draw(WIN)

        player.draw(WIN)
 
        if lost:

            lost_label = loss_font.render("YOU LOST !!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 270))

            if level == 1:
                lost1_label = lost_font.render(f"You Survived {level} Round", 1, (255,0,0))
                WIN.blit(lost1_label, (WIDTH/2 - lost1_label.get_width()/2, 390))

            if level > 1:
            
                lost2_label = lost_font.render(f"You Survived {level} Rounds", 1, (255,0,0))
                WIN.blit(lost2_label, (WIDTH/2 - lost2_label.get_width()/2, 390))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        if len(Medkit) == 0:
            
            for i in range (num):
                med = Heal(random.randrange(50, WIDTH-100),random.randrange(-1500,-100))
                Medkit.append(med)

        if len(hearts) == 0:
            
            for i in range (num1):
                heart = Heart(random.randrange(50, WIDTH-100),random.randrange(-1500,-100))
                hearts.append(heart)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel        
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        if keys[pygame.K_ESCAPE]:
            main_menu()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 20
                enemies.remove(enemy)
            
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        for med in Medkit[:]:
            med.move(med_vel)

            if HEIGHT == 900:
                Medkit.remove(med)
            
            if collide(med,player):
                player.health += 25
                Medkit.remove(med)

            if player.health >= 250:

                player.health = 250

        for heart in hearts[:]:
            heart.move(heart_beat)

            if HEIGHT == 900:
                hearts.remove(med)
            
            if collide(heart,player):
                lives += 1
                hearts.remove(heart)

            if lives > 5:

                lives -= 1

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("Berlin Sans FB", 100)
    settings_font = pygame.font.SysFont("Berlin Sans FB", 55)
    movement_font = pygame.font.SysFont("Berlin Sans FB", 40)
    play_font = pygame.font.SysFont("Berlin Sans FB", 60)
    
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("EVER", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/0.9, 150))
        title_label1 = title_font.render("SPACE", 1, (0,0,255))
        WIN.blit(title_label1, (WIDTH/2 - title_label1.get_width()/9, 150))
        click_label = play_font.render("Click To Play", 1, (0,255,0))
        WIN.blit(click_label, (WIDTH/2 - click_label.get_width()/2, 300))
        
        settings_label = settings_font.render("Controls : ", 1, (255,100,10))
        WIN.blit(settings_label, (WIDTH/2 - settings_label.get_width()/0.6, 550))
        
        up_label = movement_font.render("Move Up = W ", 1, (210,150,75))
        WIN.blit(up_label, (WIDTH/2 - up_label.get_width()/2, 460))
                                        
        left_label = movement_font.render("Move Left = A ", 1, (210,150,75))
        WIN.blit(left_label, (WIDTH/2 - left_label.get_width()/2.1, 510))
        
        down_label = movement_font.render("Move Down = S", 1, (210,150,75))
        WIN.blit(down_label, (WIDTH/2 - down_label.get_width()/2.2, 560))
        
        right_label = movement_font.render("Move Right = D ", 1, (210,150,75))
        WIN.blit(right_label, (WIDTH/2 - right_label.get_width()/2.3, 610))

        shoot_label = movement_font.render("Shoot = SpaceBar  ", 1, (210,150,75))
        WIN.blit(shoot_label, (WIDTH/2 - shoot_label.get_width()/2.65, 660))

        quit_label = movement_font.render("Quit = Escape", 1, (210,150,75))
        WIN.blit(quit_label, (WIDTH/2 - quit_label.get_width()/2, 710))
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
