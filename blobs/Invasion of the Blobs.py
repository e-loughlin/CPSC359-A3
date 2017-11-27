#! /usr/bin/env python

# 2017-09-19 - modified by JE Boyd for python3



import pygame, os, random
from pygame.locals import *

random.seed()
WORLD = Rect(0, 0, 480, 550)

def load_image(filename):
    img = pygame.image.load(os.path.join("data", filename))
    img.set_colorkey((0, 0, 0), RLEACCEL)
    return img.convert()


def load_sound(filename, volume=0.2):
    snd = pygame.mixer.Sound(os.path.join("data", filename))
    snd.set_volume(volume)
    return snd


def load_highscore():
    f = os.path.expanduser("~/.invasionoftheblobs")
    if os.path.exists(f):
        hs = open(os.path.expanduser("~/.invasionoftheblobs"), "r").read()
        return int(hs)
    else:
        hs = open(os.path.expanduser("~/.invasionoftheblobs"), "w").write(str(0))
        return 0
    
def save_highscore(score):
    open(os.path.expanduser("~/.invasionoftheblobs"), "w").write(str(score))


class Ship(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = (240, 520))
        self.reload_timer = 0
        self.reload_time  = 10
        self.shoot_sound  = load_sound("laser.wav")
        self.level = 1
        self.heat = 0
        self.overheated = False
        self.poweredup = False
        self.powertimer = 0
        self.frame = 0

    def update(self):
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if key[K_RIGHT]:
            self.rect.move_ip(5, 0)

        self.reload_timer += 1
        if key[K_SPACE] and not self.overheated:
            self.heat += 0.75
            if self.reload_timer >= self.reload_time:
                self.reload_timer = 0
                Shot(self.rect.midtop)
                if self.poweredup:
                    Shot(self.rect.midtop, 1)
                    Shot(self.rect.midtop, -1)
                self.shoot_sound.play()
        else:
            if self.heat > 0:
                self.heat -= 1

        if self.poweredup:
            self.powertimer -= 1
            if self.powertimer <= 0:
                self.poweredup = False

        if self.heat >= 100:
            self.overheated = True
        if self.overheated:
            self.heat -= 1
            if self.heat <= 0:
                self.overheated = False

        self.frame += 1
        self.image = self.images[self.frame//2%2]
        self.rect.clamp_ip(WORLD)

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.die_sound.play()
        for i in range(15):
            Particle(self.rect.center)


class Shot(pygame.sprite.Sprite):

    def __init__(self, pos, xspeed = 0):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(midbottom = pos)
        self.xspeed = xspeed

    def update(self):
        self.rect.move_ip(self.xspeed, -10)
        if not WORLD.contains(self.rect):
            self.kill()



class Star(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((2, 2))
        #self.rect = self.image.get_rect(center = (random.randrange(480), random.randrange(600)))
        self.rect = self.image.get_rect(center = (random.randrange(733), random.randrange(600)))
        self.speed = random.randrange(5, 15)
        self.color = (50+ self.speed*12, 50+ self.speed*12, 50+ self.speed*12)
        self.image.fill(self.color)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top >= 600:
            self.rect.top = 0
        

class Blob(pygame.sprite.Sprite):

    def __init__(self, pos, formation):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
        self.formation = formation
        self.frame = 0
        self.yspeed = random.randrange(1, 6)

    def update(self):
        if self.formation == 1:
            self.rect.move_ip(0, self.yspeed)
        if self.formation == 2:
            self.rect.move_ip(-2, self.yspeed)
        if self.formation == 3:
            self.rect.move_ip(2, self.yspeed)
        if self.formation == 4:
            self.rect.move_ip(-1, self.yspeed)
        if self.formation == 5:
            self.rect.move_ip(1, self.yspeed)

        if self.rect.top >= 600:
            pygame.sprite.Sprite.kill(self)
        if self.rect.left <= -100:
            pygame.sprite.Sprite.kill(self)
        if self.rect.right >= 580:
            pygame.sprite.Sprite.kill(self)

        self.frame += 1
        self.image = self.images[self.frame//2%len(self.images)]

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.die_sound.play()
        for i in range(7):
            Particle(self.rect.center)


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, pos=None, size=1):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self._image = self.image
        if not pos:
            pos = (random.randrange(20, 400), 0)
        self.rect = self.image.get_rect(center = pos)
        self.angle = 0
        self.vx = random.randrange(-3, 3)
        self.vy = random.randrange(1, 5)
        self.size = size
        if self.size == 2:
            self.image = self.image2
            self._image = self.image

    def update(self):
        self.rotate()
        self.angle += 5
        self.rect.move_ip(self.vx, self.vy)

        if self.rect.top >= 600:
            pygame.sprite.Sprite.kill(self)
        if self.rect.left <= -100:
            pygame.sprite.Sprite.kill(self)
        if self.rect.right >= 580:
            pygame.sprite.Sprite.kill(self)

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        if self.size == 1:
            Asteroid(self.rect.center, 2)
            Asteroid(self.rect.center, 2)
            Asteroid(self.rect.center, 2)

    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self._image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center


class Boss(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = []
        for img in Blob.images:
            self.images.append(pygame.transform.scale(img, (160, 160)))
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = (240, 100))
        self.frame = 0
        self.hp = 50
        self.oy = self.rect.y
        self.ys = 2

    def kill(self):
        if self.alive():
            self.hp -= 1
            if self.hp <= 0:
                pygame.sprite.Sprite.kill(self)
                for i in range(150):
                    Particle(self.rect.center)

    def update(self):
        self.frame += 1
        self.image = self.images[self.frame//10%len(self.images)]
        if not random.randrange(10):
            Blob(self.rect.center, random.randrange(1, 6))
        self.rect.move_ip(0, self.ys)
        if self.rect.y > self.oy + 220:
            self.ys = -self.ys
        if self.rect.y < self.oy:
            self.ys = -self.ys


class Particle(pygame.sprite.Sprite):

    def __init__(self, pos):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(center=pos)

        self.vx = random.randrange(-10, 10)
        self.vy = random.randrange(-10, 10)

        self.alpha = 255

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        self.alpha -= 10
        if self.alpha <= 0:
            self.kill()


class Powerup(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(center = (random.randrange(20, 460), 0))

    def update(self):
        self.rect.move_ip(0, 3)
        if self.rect.top >= 600:
            self.kill()

class Message(pygame.sprite.Sprite):

    def __init__(self, message):

        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font(os.path.join("data", "font.ttf"), 32)
        self.image = self.font.render(message, 1, (0, 255, 0))
        self.rect = self.image.get_rect(center = (240, 100))
        self.life = 100
 
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()


def formation1(num=3):
    for i in range(num):
        Blob((240, -i*32), 1) 

def formation2(num=3):
    for i in range(num):
        Blob((10 - i*32, -i*32), 3)

def formation3(num=3):
    for i in range(num):
        Blob((480+i*32, -i*32), 2)

def formation4(num=3):
    for i in range(num):
        Blob((120, -i*32), 1)

def formation5(num=3):
    for i in range(num):
        Blob((360, -i*32), 1)

def formation6(num=3):
    for i in range(num):
        Blob((120 - i*16, -i*32), 5)

def formation7(num=3):
    for i in range(num):
        Blob((360+i*16, -i*32), 4)


def playLevels(game):
    level = game.level
    if not game.blobs:
        game.level += 0.1
        lvl = game.level
        if game.level > 6.0:
            game.boss = Boss()
            return
        else:
            for i in range(int(lvl)):
                f = random.choice([formation1, formation2, formation3, formation4, formation5, formation6, formation7])
                f()


class Game:

    def __init__(self):

        pygame.display.set_caption("Invasion of the Blobs - Ludum Dare 10.5 - PyMike's Entry")
        self.screen = pygame.display.set_mode((480, 550), HWSURFACE|DOUBLEBUF)
        #self.screen = pygame.display.set_mode((733, 550), HWSURFACE|DOUBLEBUF)

        Ship.images = [load_image("ship1.bmp"), load_image("ship2.bmp")]
        Shot.image  = load_image("shot.bmp")
        Powerup.image  = load_image("powerup.bmp")
        Blob.images = [load_image("slime1.bmp"), load_image("slime2.bmp"), load_image("slime3.bmp"), load_image("slime4.bmp"), load_image("slime5.bmp"), load_image("slime6.bmp"), load_image("slime7.bmp"), load_image("slime8.bmp")]
        Asteroid.image = load_image("asteroid1.bmp")
        Asteroid.image2 = load_image("asteroid2.bmp")
        Particle.image = load_image("particle.bmp")
        Ship.die_sound = load_sound("explosion.wav", 0.3)
        Blob.die_sound = load_sound("explosion.wav", 0.3)

        self.all = pygame.sprite.RenderUpdates()
        self.bg  = pygame.sprite.RenderUpdates()
        self.blobs = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()

        Ship.containers = self.all
        Shot.containers = self.all, self.shots
        Blob.containers = self.all, self.blobs
        Asteroid.containers = self.all, self.asteroids
        Particle.containers = self.all, self.particles
        Powerup.containers = self.all, self.powerups
        Message.containers = self.all
        Boss.containers = self.all
        Star.containers = self.bg

        for i in range(60):
            Star()

        self.ship = Ship()
        self.clock = pygame.time.Clock()
        self.font  = pygame.font.Font(os.path.join("data", "font.ttf"), 16)
        self.bigfont  = pygame.font.Font(os.path.join("data", "font.ttf"), 40)
        self.hugefont  = pygame.font.Font(os.path.join("data", "font.ttf"), 80)
        self.paused = False
        self.level = 1
        self.score = 0
        self.lives = 5
        self.boss = Boss()
        self.highscore = load_highscore()
        self.gamewon = False


    def pauseLoop(self):

        while self.paused:
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    return
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.paused ^= 1
                    if e.key == K_p:
                        self.paused ^= 1

    def menuLoop(self):

        option = 1

        pygame.mixer.music.load(os.path.join("data", "loop.ogg"))
        pygame.mixer.music.play(-1)

        while 1:

            self.bg.update()
            self.clock.tick(60)

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    return
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        pygame.quit()
                        return
                    if e.key == K_p:
                        self.paused ^= 1
                    if e.key == K_DOWN:
                        option = 2
                    if e.key == K_UP:
                        option = 1
                    if e.key == K_RETURN:
                        if option == 1:
                            self.gameLoop()
                        if option == 2:
                            pygame.quit()
                            return

            self.screen.fill((0, 0, 0))
            self.bg.draw(self.screen)
            ren = self.hugefont.render("Invasion", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 50))                
            ren = self.bigfont.render("of the Blobs", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 120))  
            ren = self.font.render("PyMike's Entry for Ludum Dare 10.5", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 220))   
            ren = self.font.render("Copyright (C) 2008", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 240))
            ren = self.bigfont.render("New Game", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 360))  
            ren = self.bigfont.render("Quit Game", 1, (0, 255, 0))
            self.screen.blit(ren, (240-ren.get_width()//2, 400))
            if option == 1:
                ren = self.bigfont.render("> New Game <", 1, (255, 255, 255))
                self.screen.blit(ren, (240-ren.get_width()//2, 360)) 
            if option == 2:
                ren = self.bigfont.render("> Quit Game <", 1, (255, 255, 255))
                self.screen.blit(ren, (240-ren.get_width()//2, 400)) 
            pygame.display.flip()


    def gameLoop(self):

        self.paused = False
        self.level = 1
        self.score = 0
        self.lives = 5
        self.gamewon = False
        for s in self.all.sprites():
            pygame.sprite.Sprite.kill(s)
        playLevels(self)
        self.highscore = load_highscore()

        while 1:
            self.clock.tick(60)
            self.all.update()
            self.bg.update()
            self.pauseLoop()

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    return
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        return
                    if e.key == K_p:
                        self.paused ^= 1

            if not random.randrange(1000) and not self.ship.poweredup and not self.powerups and not self.gamewon:
                Powerup()

            if pygame.sprite.groupcollide(self.shots, self.blobs, 1, 1):
                self.score += 25
            if pygame.sprite.groupcollide(self.shots, self.asteroids, 1, 1):
                self.score += 75
            for blob in pygame.sprite.spritecollide(self.ship, self.blobs, 0):
                if self.ship.alive():
                    blob.kill()
                    self.lives -= 1
                    self.ship.kill()
                    for b in self.blobs:
                        b.kill()
                    if self.level < 6:
                        self.level -= 0.1
            for p in pygame.sprite.spritecollide(self.ship, self.powerups, 0):
                if self.ship.alive():
                    p.kill()
                    self.ship.poweredup = True
                    self.ship.powertimer = 500
                    Message("Power up!")

            for shot in pygame.sprite.spritecollide(self.boss, self.shots, 0):
                self.boss.kill()
                if self.boss.alive():
                    shot.kill()

            if not self.ship.alive() and self.lives > 0 and not self.particles and not self.gamewon:
                self.ship = Ship()

            if not self.boss.alive() and self.level >= 6:
                self.gamewon = True
            if not self.boss.alive() and not self.gamewon:
                playLevels(self)
                #if not random.randrange(120):
                    #Asteroid()

            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)

            self.screen.fill((0, 0, 0))
            self.bg.draw(self.screen)
            self.all.draw(self.screen)
            ren = self.font.render("Score: %06d" % self.score, 1, (0, 255, 0))
            self.screen.blit(ren, (10, 10))
            ren = self.font.render("Lives: %d" % self.lives, 1, (0, 255, 0))
            self.screen.blit(ren, (220, 10))
            ren = self.font.render("Level: %d" % self.level, 1, (0, 255, 0))
            self.screen.blit(ren, (400, 10))
            pygame.draw.rect(self.screen, (0, 155+self.ship.heat, 0), (360, 30, self.ship.heat, 5))
            pygame.draw.rect(self.screen, (0, 255, 0), (360, 30, 100, 5), 1)
            ren = self.font.render("High: %06d" % self.highscore, 1, (0, 255, 0))
            self.screen.blit(ren, (10, 30))
            if self.boss.alive():
                pygame.draw.rect(self.screen, (0, 255, 0), (190, self.boss.rect.bottom+20, self.boss.hp*2, 5))
                pygame.draw.rect(self.screen, (0, 255, 0), (190, self.boss.rect.bottom+20, 100, 5), 1)
            if self.ship.overheated:
                ren = self.font.render("Cooling gun...", 1, (0, 255, 0))
                self.screen.blit(ren, (240-ren.get_width()//2, 275-ren.get_height()//2))                
            if self.gamewon:
                for s in self.blobs:
                    pygame.sprite.Sprite.kill(s)
                pygame.sprite.Sprite.kill(self.ship)
                ren = self.bigfont.render("Congratulations!", 1, (0, 255, 0))
                self.screen.blit(ren, (240-ren.get_width()//2, 275-ren.get_height()//2))                
                ren = self.font.render("You saved the galaxy!", 1, (0, 255, 0))
                self.screen.blit(ren, (240-ren.get_width()//2, 300-ren.get_height()//2))                

            if self.lives <= 0:
                ren = self.bigfont.render("Game Over!", 1, (0, 255, 0))
                self.screen.blit(ren, (240-ren.get_width()//2, 275-ren.get_height()//2))                
            pygame.display.flip()


def run():
    pygame.init()
    game = Game()
    game.menuLoop()


if __name__ == "__main__":
    run()
