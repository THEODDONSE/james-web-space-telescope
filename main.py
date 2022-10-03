import pygame
import os
import time
import random
pygame.font.init()
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JWST")
pygame.display.set_icon(pygame.transform.scale(pygame.image.load("assets/jwst-3.png").convert_alpha(),(32,32)))

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
jwst1=pygame.transform.scale(pygame.image.load(os.path.join("assets","jwst-1.png")),(862/4.5,400/4.5))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
hubble=[[pygame.transform.scale(pygame.image.load(os.path.join("assets", "all3-hubble.png")),(WIDTH*1.25,HEIGHT*1.3)),(-100,-205)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "hubble.jpg")),(WIDTH,231*2.5-50)),(0,0)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "deepfieldhubble.jpg")),(WIDTH,231*2.5-50)),(0,0)]]
# Player player
nircam=[[pygame.transform.scale(pygame.image.load(os.path.join("assets", "all3-nir.png")),(WIDTH*1.25,HEIGHT*1.25)),(-135,-200)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "ring-nir.png")),(862*3,400*1.3)),(-550,3)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "nircamdeep.jpg")),(862*3,400*1.3+10)),(0,0)]]
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")),(100,90))
JWST = pygame.transform.flip(pygame.transform.scale(pygame.image.load(os.path.join("assets", "jwst-2.png")),(860/8,873/8)),True,False)
mircam=[[pygame.transform.scale(pygame.image.load(os.path.join("assets", "all3-mir.png")),(WIDTH*1.15,HEIGHT*1.15)),(-140,-170)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "ring-mir.png")),(WIDTH*1.95,HEIGHT-198)),(-562,7)],[pygame.transform.scale(pygame.image.load(os.path.join("assets", "mirdeep.png")),(WIDTH*1.95,HEIGHT-196)),(-562,3)]]
# Lasers
RED_LASER = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "pixel_laser_red.png")))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "controlpannel.jpg")), (WIDTH*1.25, HEIGHT*1.25))

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

    def off_screen(self):
        return not(self.y <= 510 and self.y >= 0)

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
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
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
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen():
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
        self.color=color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
class Jwst:
    def __init__(self,image,x,y):
        self.image=image
        self.info=0
        self.x,self.y=x,y
        self.mask=pygame.mask.from_surface(self.image)
        self.mode="hubble"
        self.vel=0
    def move(self,fgs):
        if not fgs:
            self.x+=self.vel

    def draw(self):
        WIN.blit(self.image,(self.x,self.y))

        
def main():
    run = True
    mode="hubble"
    game=True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 30)
    cosmic_light=[]
    enemies = []
    wave_length = 5
    enemy_vel = 1

    spectrum="red"
    player_vel = 6
    laser_vel = 8
    instrument=False
    player = Player(600, 275)
    jwst=Jwst(JWST,600,400)
    clock = pygame.time.Clock()
    fgs=False
    lost = False
    lost_count = 0
    pressed1=False
    pressed2=False
    pressed1_time=None
    pressed2_time=None
    esc=False
    esc_time=pygame.time.get_ticks()
    def redraw_window():
        WIN.blit(BG, (-165,-70))

        if level==1 and mode=="hubble":
            WIN.blit(hubble[0][0],hubble[0][1])
        if level==1 and mode=="nir":
            WIN.blit(nircam[0][0],nircam[0][1])
        if level==1 and mode=="mir":
            WIN.blit(mircam[0][0],mircam[0][1])
        if level==2 and mode=="hubble":
            WIN.blit(hubble[1][0],hubble[1][1])
        if level==2 and mode=="nir":
            WIN.blit(nircam[1][0],nircam[1][1])
        if level==2 and mode=="mir":
            WIN.blit(mircam[1][0],mircam[1][1])
        if level==3 and mode=="hubble":
            WIN.blit(hubble[2][0],hubble[2][1])
        if level==3 and mode=="nir":
            WIN.blit(nircam[2][0],nircam[2][1])
        if level==3 and mode=="mir":
            WIN.blit(mircam[2][0],mircam[2][1])
        if level!=3:
            for enemy in enemies:
                if level==1 and (mode=="nir"or mode=="mir") and jwst.info>=50:
                    enemy.draw(WIN)
                if level==2 and (instrument or fgs) and( mode=="nir"or mode=="mir") and jwst.info>=75 and enemy.color==spectrum:
                    if fgs and abs(-enemy.x+jwst.x)<jwst.image.get_width() and abs(jwst.y-enemy.y)<510:
                        enemy.draw(WIN)
                    else:
                        enemy.draw(WIN)
        for photon in cosmic_light:
            photon.draw(WIN)
            photon.move(10)
            if photon.y>420:
                cosmic_light.remove(photon)
        if instrument:
            if level !=3:
                image=pygame.Surface((WIDTH,510))
                if spectrum=="red":
                    image.fill((255,0,0))
                if spectrum=="green":
                    image.fill((0,255,0))
                if spectrum=="blue":
                    image.fill((0,0,255))
                WIN.blit(image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
            if level==3 and jwst.info>=100:
                image=pygame.Surface((WIDTH,510))
                if spectrum=="red":
                    image.fill((255,0,0))
                if spectrum=="green":
                    image.fill((0,255,0))
                if spectrum=="blue":
                    image.fill((0,0,255))
                WIN.blit(image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        if fgs and not instrument:
                image=pygame.Surface((JWST.get_width(),510))
                if spectrum=="red":
                    image.fill((255,0,0))
                if spectrum=="green":
                    image.fill((0,255,0))
                if spectrum=="blue":
                    image.fill(0,0,255)
                WIN.blit(image, (jwst.x,0), special_flags = pygame.BLEND_RGBA_MULT)

        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        player.draw(WIN)
        jwst.draw()

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        extra()
        pygame.display.update()
    def extra():
        WIN.blit(jwst1,(-52,75))
        pygame.draw.rect(WIN, "white", (100, 100, 200, 25))
        pygame.draw.rect(WIN, "#FFD700", (100, 100, 200 * (jwst.info/100),25))
        
        
        
                

                
    
    while run:
        if game:
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
            if jwst.info>=100:
                jwst.info=100
            if len(enemies) == 0 and level!=3:
                level += 1
                title_font = pygame.font.SysFont("comicsans", 12)
                if level==1:
                    level_label=title_font.render("USE NIRCAM OR MIRCAM TO SPOT THE ALIENS BY 2 OR 3", 1, (255,255,255))
                    WIN.blit(level_label, (WIDTH/2 - level_label.get_width()/2, 200))
                if level==2:
                    level_label=title_font.render("THESE ALIENS ARE MORE SMARTER SO THEY ARE ONLY ALOWWING SOME SPECTRA OF INFRARED LIHT TO REFLECT USE NIRSpec -4 TO FIND THEM BY THEIR CHEMICAL OMPOSITION ", 1, (255,255,255))
                    level_label1=title_font.render("USE R FOR HYDROGEN B FOR OXYGEN AND G FOR NITROGEN",1,(255,255,255))
                    WIN.blit(level_label, (WIDTH/2 - level_label.get_width()/2, 200))
                    WIN.blit(level_label1, (WIDTH/2 - level_label.get_width()/2, 400))
                if level==3:
                    level_label1=title_font.render("THE SCIENTIST AT EARTH HAVE FOUND THE CHEMICAL COMPOSTION OF ALIENS BY SO THEY HAVE FOUND THE COMPOSTION OF GALAXY THEY BELONG TO- ",1,(255,255,255))
                    level_label2=title_font.render("THE GALAXY IS RICH IN HYDROGEN SO IT FALLS IN THE RED SPECTRA OF INFRARED USE JWST TO LOCATE IT",1,(255,255,255))
                    level_label3=title_font.render("USE FGS INSTRUMENT BY PRESSING 5 FOR ACCURACY COMBINED WITH NIRSPEC (R,G,B)",1,(255,255,255))
                    WIN.blit(level_label1, (WIDTH/2 - level_label.get_width()/2, 350))
                    WIN.blit(level_label2, (WIDTH/2 - level_label.get_width()/2, 400))
                    WIN.blit(level_label3, (WIDTH/2 - level_label.get_width()/2, 500))
                pygame.time.delay(5000)
                jwst.info=0
                if level !=3:
                    wave_length += 5
                    for i in range(wave_length):
                        enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1200, -100), random.choice(["red", "blue", "green"]))
                        enemies.append(enemy)

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
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < 300: # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()
            if keys[pygame.K_LEFT] and jwst.x - jwst.vel > 0: # left
                if not fgs:
                    jwst.vel =-7
                else:
                    jwst.x-=7

            elif keys[pygame.K_RIGHT] and jwst.x + jwst.vel + jwst.image.get_width() < WIDTH: # right
                if not fgs:
                    jwst.vel = 7
                else:
                    jwst.x+=7
            if jwst.x+jwst.vel<0 or jwst.x+jwst.vel+jwst.image.get_width()>WIDTH:
                jwst.vel*=-1
            if keys[pygame.K_1]:
                mode="hubble"
            elif keys[pygame.K_2]:
                mode="nir"
            elif keys[pygame.K_3]:
                mode="mir"
            elif keys[pygame.K_4] and not pressed2 and not fgs:
                instrument=not instrument
                pressed2_time=pygame.time.get_ticks()
                pressed2=True
            elif keys[pygame.K_5]and not pressed1 and not instrument:
                fgs=not fgs
                pressed1_time=pygame.time.get_ticks()
                pressed1=True
            if pressed1:
                current_time=pygame.time.get_ticks()
                if current_time-pressed1_time>300:
                    pressed1=False
            if pressed2:
                current_time=pygame.time.get_ticks()
                if current_time-pressed2_time>300:
                    pressed2=False
            if keys[pygame.K_ESCAPE]and not esc:
                esc=True
                esc_time=pygame.time.get_ticks()
                game=not game
            if esc:
                current_time=pygame.time.get_ticks()
                if current_time-esc_time>=500:
                        esc=False
            
            jwst.move(fgs)
            if instrument or fgs:
                if keys[pygame.K_r]:
                    spectrum="red"
                if keys[pygame.K_g]:
                    spectrum="green"
                if keys[pygame.K_b]:
                    spectrum="blue"

            if random.randrange(0, 20) == 1:
                    photon=Laser(random.randrange(0,1200),random.randrange(-500,0),random.choice([RED_LASER,GREEN_LASER,BLUE_LASER]))
                    cosmic_light.append(photon)
            for enemy in enemies:
                enemy.move(enemy_vel)
                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > 510:
                    lives -= 1
                    enemies.remove(enemy)
            for photon in cosmic_light:
                if collide(jwst,photon):
                    jwst.info +=10
                    cosmic_light.remove(photon)
            player.move_lasers(-laser_vel, enemies)
            if level==3:
                rect=pygame.Rect(900,90,40,40)
                if pygame.mouse.get_pressed()[0]:
                    if pygame.Rect.collidepoint(rect,pygame.mouse.get_pos()):
                        win=title_font.render("YOU WON", 1, (255,255,255))
                        WIN.blit(win, (WIDTH/2 - level_label.get_width()/2, 400))
                        pygame.time.dealy(5000)
                        quit()
        else:
            if  esc:
                current_time=pygame.time.get_ticks()
                if current_time-esc_time>=3000:
                        esc=not esc
            keys=pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]and not esc:
                    game=not game
                    esc_time=pygame.time.get_ticks()
                    esc=not esc
            

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 12)
    run = True
    while run:
        WIN.fill("black")
        WIN.blit(BG, (-165,-70))
        
        title_label = title_font.render("THE EARTH IS BEING INVADED BY ALIENS THE SPACE FORCE HAS BEEN DEPLOYED, BUT THESE ALIENS ARE SMART AND CAN'T BE DETECTED IN VISIBLE LIGHT USE THE JWST TO HELP THE PILOT", 1, (255,255,255))
        next_label = title_font.render("Press mouse to begin!", 1, (255,255,255))
        label_2=title_font.render("USE W,A,S,P TO CONTROL PILOT AND LEFT,RIGHT ARROW KEY TO CONTROL JWST COLLECT LIGHT FIRST FOR ENOUGH DATA FOR JWST" ,1, (255,255,255))
        label_3=title_font.render("PRESS 1 FOR VISIBLE SPECTRUM ", 1, (255,255,255))
        label_4=title_font.render("PRESS 2 FOR NIRCam ", 1, (255,255,255))
        label_5=title_font.render("PRESS 3 FOR MIRI", 1, (255,255,255))
        label_6=title_font.render("PRESS 4 FOR NIRSpec ", 1, (255,255,255))
        label_7=title_font.render("PRESS 5 FOR FGS ", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
