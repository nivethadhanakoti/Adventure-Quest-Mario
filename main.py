import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
import heapq
import math
import random

pygame.init()

pygame.display.set_caption("MarioBros")

BG_COLOR = (255,255,255)
WIDTH, HEIGHT  = 1000,800
FPS = 60
PLAYER_VEL = 5


# Load start image
def get_start_screen():
    start_image = pygame.image.load("assets/background/start.png")  # Load your start image from path
    start_image = pygame.transform.scale(start_image, (WIDTH, HEIGHT))  # Scale to fit the screen
    return start_image

# Function to draw start text
def draw_start_text(win):
    x = WIDTH // 2  # Center the image horizontally
    y = HEIGHT // 2 + 50
    start_img = pygame.image.load("assets/addons/start.png")
    start_text_rect = start_img.get_rect(topleft=(x - 110, y - 36))  # Get rectangle for detecting clicks
    win.blit(start_img, (x - 300, y - 10))
    return start_text_rect

def game_end_check(player, last_block, coins):
    if player.rect.colliderect(last_block.rect) and player.all_coins_collected(coins):
        # Show the game ending screen
        display_end_screen()

def display_end_screen():
    # Load and display the "end.png" image
    end_img = pygame.image.load("assets/background/end.png")
    end_img = pygame.transform.scale(end_img, (WIDTH, HEIGHT))
    window.blit(end_img, (0, 0))
    pygame.display.update()
    pygame.time.wait(3000)  # Wait for 3 seconds before closing or restarting
    pygame.quit()
    exit()  # End the game


window = pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("assets" , dir1 ,dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width): #divide to find number of images
            surface = pygame.Surface((width,height) , pygame.SRCALPHA , 32)
            rect = pygame.Rect(i * width, 0 ,width, height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)

        else:
            all_sprites[image.replace(".png","")] = sprites
    return all_sprites


def get_block(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA,32)
    rect = pygame.Rect(96, 0 ,size, size)
    surface.blit(image, (0,0) ,rect)
    return pygame.transform.scale2x(surface)



class Player(pygame.sprite.Sprite): #Sprite object
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3
    

    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = 'left'
        self.animation_count = 0
        self.fall_count = 0 #for gravity
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.coins = 0
        self.health = 100

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

        
    def make_hit(self,hit_type):
        self.hit = True
        self.hit_count = 0
        if hit_type == 'fire':
            if self.health > 0:
                self.health -= 1 
        else:
            if self.health > 0:
                self.health -= 2


    
    def move(self,dx,dy):
        self.rect.x += dx #dist move to x axis
        self.rect.y += dy #dist move to y axis

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0


    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0
    
    def loop(self,fps): #update animation and stuff per frame
        self.y_vel += min(1,(self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel,self.y_vel)

        if self.hit:
            self.hit_count +=1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1


    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.hit:
            sprite_sheet = 'hit'
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = 'jump'
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = 'fall'
        elif self.x_vel != 0:
            sprite_sheet = 'run'


        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        self.update()

    def all_coins_collected(self, coins):
        # Check if all coins are collected
        for coin in coins:
            if not coin.collected:
                return False
        return True

    def draw(self,win,offset_x):
        win.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x,self.rect.y))

class Block(Object):
    def __init__(self, x,y,size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Coins:
    ANIMATION_DELAY = 10  # Adjust delay for coin animation speed

    def __init__(self, x, y, width=16, height=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.coin_sprites = [
            pygame.transform.scale2x(pygame.image.load(join("assets/coins", f"coin{i}.png")).convert_alpha())
            for i in range(2)
        ]
        self.image = self.coin_sprites[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.collected = False  

    def collect(self):
        self.collected = True

    def loop(self):
        if not self.collected:
            # Animate the coin if it hasn't been collected
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.coin_sprites)
            self.image = self.coin_sprites[sprite_index]
            self.animation_count += 1

            if self.animation_count // self.ANIMATION_DELAY >= len(self.coin_sprites):
                self.animation_count = 0

    def draw(self, win, offset_x):
        if not self.collected:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Enemy(pygame.sprite.Sprite):
    ANIMATION_DELAY = 10  # Delay between frames for animation

    def __init__(self, x, y, width=32, height=32):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.enemy_sprites = load_sprite_sheets("MainCharacters", "MaskDude", width, height, True)
        self.image = self.enemy_sprites["idle_right"][0]  # Assuming "fall" animation is available
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.direction = 'right'
        self.speed = 2
        self.path = None
        self.frame_count = 0
        self.path_interval = 5 * FPS
        self.path_counter = 1000
        self.previous_moves = []

        self.temperature = 100  # Initial "temperature" for annealing
        self.cooling_rate = 0.995

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0


    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def heuristic(self,pos1,pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two points"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def collision(self, node, objects):
        """Check if moving to a position causes a collision."""
        prev_x, prev_y = self.rect.x, self.rect.y
        self.rect.x = node[0]
        self.rect.y = node[1]
        
        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                self.rect.x, self.rect.y = prev_x, prev_y
                return True  # Blocked by an object
                
        self.rect.x, self.rect.y = prev_x, prev_y
        return False  # No collision

    def move_local(self, player, objects):
        node = (self.rect.x, self.rect.y)
        goal_state = (player.rect.x, player.rect.y)
        
        moves = {
            'right': (node[0] + self.speed, node[1]),
            'left': (node[0] - self.speed, node[1]),
            'down': (node[0], node[1] + self.speed),
            'up': (node[0], node[1] - self.speed)
        }
        
        best_move = None
        current_heuristic = float('inf')
        
        for move, neigh in moves.items():
            if not self.collision(neigh, objects):
                heuristic = self.heuristic(neigh, goal_state)
                if heuristic < current_heuristic:
                    best_move = neigh
                    current_heuristic = heuristic
        
        if best_move:
            self.rect.x = best_move[0]
            self.rect.y = best_move[1]
    
    def loop(self, player,objects):
        # Handle animation frame update
        sprite_sheet_name = f"run_{self.direction}"
        sprites = self.enemy_sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
            self.animation_count = 0

        # Move the enemy
        #self.move(player,objects)
        self.move_local(player,objects)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

def get_background(name):
    pass
    image = pygame.image.load(join("assets/background/",name))
    image = pygame.transform.scale(image, (WIDTH, HEIGHT)) # scaling an image to fit display window
    return image


def draw_health_bar(window, health):
    
    max_health = 100  
    bar_width = 200
    bar_height = 20
    border_color = (0, 0, 0)  
    fill_color = (255, 0, 0)  

    

    # Calculate bar position (top-right corner)
    x = WIDTH - bar_width - 20  # 20px padding from the right
    y = 20  # 20px padding from the top

    pygame.draw.rect(window, border_color, (x - 4, y - 4, bar_width + 8, bar_height + 8),4)

    # Calculate filled portion width
    filled_width = int((health / max_health) * bar_width)

    # Draw the filled red health bar inside the border
    pygame.draw.rect(window, fill_color, (x, y, filled_width, bar_height))

    health_img = pygame.image.load("assets/addons/health2.png")
    window.blit(health_img,(x - 110, y - 36))



    


def handle_vertical_collision(player, objects,dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()

            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx , 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx,0)
    player.update()
    return collided_object

def collide_with_enemy(player, enemy):
    if pygame.sprite.collide_mask(player, enemy):
        player.make_hit("enemy")  # Reduce health on collision with enemy


def coins_collect(player, coins):
    for coin in coins:
        if pygame.sprite.collide_mask(player, coin) and coin.collected == False:
            coin.collected = True
            return coin

    return None       
            



def check_death(player):
    if player.health <= 0:
        return True
    
    if player.rect.y > 1010:
        return True
    
    return False

# Update draw function to render enemies
def draw(window, background, player, objects, coins, enemy, offset_x):
    window.blit(background, (0, 0))

    for obj in objects:
        obj.draw(window, offset_x)
    for coin in coins:
        coin.draw(window, offset_x)
    
    enemy.draw(window, offset_x)
    draw_health_bar(window, player.health)
    player.draw(window, offset_x)

    pygame.display.update()

def manhattan(pos1,pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def collision(node,objects):
    #prev_x, prev_y = self.rect.x, self.rect.y
    x = node[0]
    y = node[1]
    
    for obj in objects:
        if obj.rect.collidepoint(node):
            return True

    return False

def find_local_path(player_pos,enemy,objects):
    start = (enemy.rect.x,enemy.rect.y)
    goal_state = player_pos
    path = [start]
    explored = set()

    found = False
    while not(found):
        node = path[len(path) - 1]
        explored.add(node)

        neighbours = [(node[0] + 1,node[1]),(node[0],node[1] + 1),(node[0] - 1,node[1]),(node[0],node[1] - 1)]
        current_heuristic = float('inf')
        best_move = None
        for neigh in neighbours:
            if neigh not in explored and not(collision(neigh,objects)):

                if neigh == goal_state:
                    path.append(neigh)
                    break
                heuristic = manhattan(neigh,goal_state)
                if heuristic < current_heuristic:
                    current_heuristic = heuristic
                    best_move = neigh
        if best_move:
            path.append(best_move)
        else:
            break

    return path


def handle_move(player, objects, enemy):
    keys = pygame.key.get_pressed()

    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    player.x_vel = 0
    if  keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)

    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects,player.y_vel)
    to_check = [collide_left,collide_right,*vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit("fire")

    if coins_collect(player,coins) != None:
        player.coins += 1
        if player.coins == 5:
            print("All coins") # here is where you add function after getting all coins

    collide_with_enemy(player,enemy)
        

block_size = 96
player = Player(100,100,50,50)

floor = [
    Block(i * block_size, HEIGHT - block_size, block_size)
    for i in range(-WIDTH // block_size, (WIDTH * 3) // block_size)
    if i != 19 and i != 20   # Skip blocks at i = 3, 4, and 5 after the last air block
]

fire_list=[
    Fire(400,HEIGHT - block_size - 64,16,32),
    Fire(900,HEIGHT - block_size - 64,16,32),
    Fire(1200,HEIGHT - block_size - 64,16,32),
    Fire(2150,HEIGHT - block_size - 64,16,32),
    Fire(2800,HEIGHT - block_size - 64,16,32)
]

blocks_list = [
    Block(0, HEIGHT - block_size * 2,block_size),
    Block(0, HEIGHT - block_size * 3,block_size),
    Block(0, HEIGHT - block_size * 4,block_size),
    Block(0, HEIGHT - block_size * 5,block_size),
    Block(0, HEIGHT - block_size * 6,block_size),
    Block(0, HEIGHT - block_size * 7,block_size),
    Block(0, HEIGHT - block_size * 8,block_size)
    ]

air_blocks = [
    Block(200, HEIGHT - block_size * 3, block_size),  
    Block(500, HEIGHT - block_size * 5, block_size),  
    Block(600, HEIGHT - block_size * 5, block_size),  
    Block(700, HEIGHT - block_size * 5, block_size),  
    Block(1000, HEIGHT - block_size * 7, block_size),  
    Block(1400, HEIGHT - block_size * 5, block_size), 
    Block(1500, HEIGHT - block_size * 5, block_size), 
    Block(2400, HEIGHT - block_size * 3, block_size), 
    Block(2600, HEIGHT - block_size * 5, block_size), 
    Block(2700, HEIGHT - block_size * 5, block_size)
]

objects = [*floor,*blocks_list,*air_blocks,*fire_list]

coins = [
    Coins(500, HEIGHT - block_size  - 60, 16, 28),
    Coins(600, HEIGHT - block_size *5 - 60, 16, 28),
    Coins(1500, HEIGHT - block_size *5 - 60, 16, 28),
    Coins(2500, HEIGHT - block_size *5 - 60, 16, 28),
    Coins(2700, HEIGHT - block_size *5 - 60, 16, 28)
]

enemy = Enemy(300, 50)

def main(window):

    clock = pygame.time.Clock()
    run = True
    # Start screen loop
    while run:
        clock.tick(FPS)
        window.fill(BG_COLOR)

        # Draw start screen
        window.blit(get_start_screen(), (0, 0))

        # Draw START text
        start_text_rect = draw_start_text(window)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit the game if the window is closed

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button click
                    if start_text_rect.collidepoint(event.pos):  # Check if click was on the "START" text
                        run = False  # Exit the start screen to start the game

            if run == False:  
                pass

        pygame.display.update()

    background = get_background("image.png") # call function to get bg image from 
    game_counter = 0
    #defining a player
    for fire in fire_list:
        fire.on()

    scroll_area_width = 300
    offset_x = 0
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
        player.loop(FPS) #continually set movement 
        
        enemy.loop(player,objects)
        for fire in fire_list:
            fire.loop()
        for coin in coins:
            coin.loop()
        handle_move(player, objects, enemy) #set direction of movement
        last_block = floor[-1]
        game_end_check(player, last_block, coins)
        
        if (check_death(player)):
            break
        draw(window,background,player,objects,coins,enemy,offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit() 

if __name__  == '__main__':
    main(window)