#! /usr/bin/env python3

# Pysteroids - By Andrew Groeneveldt
# October 12, 2017


import pygame, os, random
from pygame.locals import *


all_sprites = pygame.sprite.Group()
shots = pygame.sprite.Group()
rocks = pygame.sprite.Group()


def load_image(filename):
    """Load an image from file
    takes: an image filename
    returns: a converted image object
    assumes: file is in local subdirectory data/
             image has transparency
    """
    image = pygame.image.load(os.path.join("data", filename))
    return image.convert_alpha()


def rotate_ip(self, angle):
    """ Rotate an image about its center
    takes: self, angle
    returns: new image
    assumes: aspect ratio of 1:1
    """
    location = self.rect.center
    new_image = pygame.transform.rotate(self.base_image, angle)
    self.rect = new_image.get_rect(center=location)
    return new_image


class Rock(pygame.sprite.Sprite):
    """Class to represent and control asteroids"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = load_image('rock.png')
        self.image = self.base_image
        self.area = pygame.display.get_surface().get_rect()
        start_x = random.randrange(self.area.width/2) - (self.area.width/4)
        start_y = random.randrange(self.area.height/2) - (self.area.height/4)
        if start_x < 0:
            start_x += self.area.width
        if start_y < 0:
            start_y += self.area.height
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.velocity = pygame.math.Vector2(random.randrange(4)-2, random.randrange(4)-2)
        self.heading = pygame.math.Vector2(0, -1)
        self.tumble = random.randrange(8)-4

    def update(self):
        """update action of rocks"""
        # tumble
        self.heading.rotate_ip(self.tumble)
        self.image = rotate_ip(self, self.heading.angle_to(pygame.math.Vector2(0, -1)))
        # move
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        # screen wrap
        if self.rect.x + self.rect.width < 0:
            self.rect.x = self.area.width
        if self.rect.y + self.rect.height < 0:
            self.rect.y = self.area.height
        if self.rect.x > self.area.width:
            self.rect.x = -self.rect.width
        if self.rect.y > self.area.height:
            self.rect.y = -self.rect.height
        

class Shot(pygame.sprite.Sprite):
    """Class to represent and control projectiles"""

    def __init__(self, position, heading):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = load_image('shot.png')
        self.image = self.base_image
        self.area = pygame.display.get_surface().get_rect()
        self.rect = self.image.get_rect(center=position)
        self.heading = heading
        self.image = rotate_ip(self, self.heading.angle_to(pygame.math.Vector2(0, -1)))
        self.velocity = heading * 20
        self.rect.move_ip(self.velocity.x, self.velocity.y)

    def update(self):
        """ update shot position """
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        if not self.area.contains(self.rect):
            self.kill()


class Ship(pygame.sprite.Sprite):
    """Class to represent and control player ship"""
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = load_image('ship.png')
        self.image = self.base_image
        self.area = pygame.display.get_surface().get_rect()
        start_x = self.area.width/2
        start_y = self.area.height/2
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.velocity = pygame.math.Vector2()
        self.heading = pygame.math.Vector2(0, -1)
        self.cooldown = 0

    def update(self):
        """ update ship heading, speed, and position """
        key = pygame.key.get_pressed()

        if self.cooldown > 0:
            self.cooldown -= 1
        
        # read keyoard input
        if key[K_LEFT]:
            self.heading.rotate_ip(-5)
            self.image = rotate_ip(self, self.heading.angle_to(pygame.math.Vector2(0, -1)))
        if key[K_RIGHT]:
            self.heading.rotate_ip(5)
            self.image = rotate_ip(self, self.heading.angle_to(pygame.math.Vector2(0, -1)))
        if key[K_UP]:
            self.velocity = self.velocity + (self.heading/5)
        if key[K_SPACE] and self.cooldown == 0:
            shot = Shot(self.rect.center, self.heading)
            shots.add(shot)
            all_sprites.add(shot)
            self.cooldown = 5
        
        # move ship
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        
        # wrap screen
        if self.rect.x + self.rect.width < 0:
            self.rect.x = self.area.width
        if self.rect.y + self.rect.height < 0:
            self.rect.y = self.area.height
        if self.rect.x > self.area.width:
            self.rect.x = -self.rect.width
        if self.rect.y > self.area.height:
            self.rect.y = -self.rect.height


def main():
    """run the game"""
    # initialization and setup
    pygame.init()
    random.seed()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Pysteroids')

    background = load_image('stars.png')
    screen.blit(background, (0, 0))
    
    ship = Ship()
    ship.add(all_sprites)
    for i in range(10):
        rock = Rock()
        rock.add(all_sprites)
        rock.add(rocks)

    # game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return

        all_sprites.update()
        pygame.sprite.groupcollide(shots, rocks, True, True)
        if pygame.sprite.spritecollideany(ship, rocks):
            ship.kill()
        
        all_sprites.clear(screen, background)
        all_sprites.draw(screen)
        pygame.display.flip()
    

if __name__ == '__main__': main()
pygame.quit()
exit()
