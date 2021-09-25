# Importing required libraries
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import sys
import math
import random
import time

# PyGame initialization
pygame.init()
vec = pygame.math.Vector2

# Display
disWidth = 1920
disHeight = 1080
display = pygame.display.set_mode((disWidth, disHeight))
pygame.display.set_caption('ForceR')
icon_of_game = pygame.image.load('Images\\ForceR_icon.png')
pygame.display.set_icon(icon_of_game)
clock = pygame.time.Clock()

# CLasses


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.fric = 0.95
        self.list_of_images = []
        for i in range(22):
            self.list_of_images.append(pygame.image.load('Images\\FliXin_image_{}.png'.format(i)))
        self.current_animation = 0
        self.animate = True
        self.attack_image = pygame.image.load('Images\\FliXin_attack_image.png')
        self.now_image = self.list_of_images[int(self.current_animation)]
        self.attack_animation_shutdown = 0
        self.rect = self.now_image.get_rect()
        self.hitted = False
        self.hitted_image = pygame.image.load('Images\\FliXin_hit_image.png')
        self.hit_timer = 0
        self.attacking = False

    def main(self):
        global display
        self.vel *= self.fric
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x > disWidth:
            self.pos.x = disWidth
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > disHeight:
            self.pos.y = disHeight
        image_copy = self.rotate()
        self.rect = image_copy.get_rect()
        self.rect.center = self.pos
        display.blit(image_copy, (self.pos.x - int(image_copy.get_width()/2),
                                  self.pos.y - int(image_copy.get_height()/2)))
        self.attack_animation()
        self.hit()
        self.update()

    def rotate(self):
        self.now_image = pygame.transform.scale(self.now_image, (121, 78))
        mousex, mousey = pygame.mouse.get_pos()
        rel_x, rel_y = mousex - self.pos.x, mousey - self.pos.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        image_copy = pygame.transform.rotate(self.now_image, angle - 90)
        return image_copy

    def attack_animation(self):
        if not self.animate and not self.hitted:
            if self.attack_animation_shutdown < 1:
                self.attack_animation_shutdown += 0.2
                self.now_image = self.attack_image
            else:
                self.attack_animation_shutdown = 0
                self.animate = True

    def update(self):
        if self.animate:
            self.current_animation += 0.2
            if self.current_animation >= len(self.list_of_images):
                self.current_animation = 0
            self.now_image = self.list_of_images[int(self.current_animation)]

    def hit(self):
        if not self.animate and self.hitted:
            if self.hit_timer < 1:
                self.hit_timer += 0.12
                self.now_image = self.hitted_image
            else:
                self.hit_timer = 0
                self.animate = True
                self.hitted = False


class Cursor:
    def __init__(self):
        self.game = True
        self.image_game = pygame.image.load('Images\\cursor_game.png')

    def main(self):
        global display
        if self.game:
            pygame.mouse.set_visible(False)
            mousex, mousey = pygame.mouse.get_pos()
            center_x = mousex - self.image_game.get_width()//2
            center_y = mousey - self.image_game.get_height()//2
            display.blit(self.image_game, (center_x, center_y))
        else:
            pygame.mouse.set_visible(True)


class PlayerBullet(pygame.sprite.Sprite):
    speed = 15

    def __init__(self, x, y, mousex, mousey):
        super().__init__()
        self.image = pygame.image.load('Images\\player_bullet.png')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.mouse_x = mousex
        self.mouse_y = mousey
        self.hit_sound = pygame.mixer.Sound('Images\\Bullet_Hit.wav')
        self.angle = math.atan2(self.y - self.mouse_y, self.x - self.mouse_x)
        self.x_vel = math.cos(self.angle+0.019) * PlayerBullet.speed
        self.y_vel = math.sin(self.angle+0.019) * PlayerBullet.speed

    def main(self):
        global display, disWidth, disHeight, vec
        self.x -= int(self.x_vel)
        self.y -= int(self.y_vel)
        self.rect.center = vec(self.x, self.y)
        display.blit(self.image, (self.x, self.y))
        if self.x < 0:
            self.kill()
        if self.x > disWidth:
            self.kill()
        if self.y < 0:
            self.kill()
        if self.y > disHeight:
            self.kill()
        self.check_for_collision()

    def check_for_collision(self):
        global asteroid_group, statistics
        hits = pygame.sprite.spritecollide(self, asteroid_group, False)
        if hits:
            self.kill()
            for aster in hits:
                aster.kill()
                self.hit_sound.play()
                if statistics.mana <= 95:
                    statistics.mana += 5
                else:
                    statistics.mana = 100
                statistics.score += 4
                manager.wave_asteroids -= 1


class Statistics:
    def __init__(self):
        self.health = 5
        self.mana = 0
        self.wave = 1
        self.font = pygame.font.SysFont('agencyfb', 32)
        self.mana_shutdown = 0
        self.score = 0
        self.may_heal = 'You can heal 1 point of health, or use ultimate power'

    def render(self):
        global display, timer
        health_rendered = self.font.render('Health: '+str(self.health), True, (255, 255, 255))
        display.blit(health_rendered, (0, 0))
        mana_rendered = self.font.render('Mana: '+str(self.mana)+'%', True, (255, 255, 255))
        display.blit(mana_rendered, (0, 42))
        score_rendered = self.font.render('Score: '+str(self.score), True, (255, 255, 255))
        display.blit(score_rendered, (0, 84))
        if timer >= 180:
            wave_rendered = self.font.render('Wave: ' + str(self.wave), True, (255, 255, 255))
            display.blit(wave_rendered, (0, 126))
        self.able_to_heal()
        self.update_mana()

    def update_mana(self):
        global playerGroup
        if player in playerGroup:
            if self.mana < 100:
                self.mana_shutdown += 0.01
                if self.mana_shutdown >= 1:
                    self.mana += 1
                    self.mana_shutdown = 0

    def able_to_heal(self):
        global display, disHeight
        if self.mana >= 100:
            may_heal_rendered = self.font.render(self.may_heal, True, (255, 255, 255))
            display.blit(may_heal_rendered, (0, disHeight-62))


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, playerx, playery, sped):
        super().__init__()
        global disWidth, disHeight
        self.original_image = pygame.image.load('Images\\asteroid_1.png')
        self.rect = self.original_image.get_rect()
        self.angle_rotate = 1
        self.speed = sped
        self.y_end = playery
        self.x_end = playerx
        self.hit_sound = pygame.mixer.Sound('Images\\Player_Hit.wav')
        choice1 = random.randint(0, 1)
        choice2 = random.randint(0, 1)
        if choice1 == 0:
            self.x_start = random.randint(-4, disWidth+4)
            if choice2 == 0:
                self.y_start = -4
            elif choice2 == 1:
                self.y_start = disHeight+4
        elif choice1 == 1:
            self.y_start = random.randint(-4, disHeight+4)
            if choice2 == 0:
                self.x_start = -4
            elif choice2 == 1:
                self.x_start = disWidth+4
        angle = math.atan2(self.y_start - self.y_end, self.x_start - self.x_end)
        self.x_vel = math.cos(angle + 0.019) * self.speed
        self.y_vel = math.sin(angle) * self.speed

    def main(self):
        global display, vec
        self.x_start -= int(self.x_vel)
        self.y_start -= int(self.y_vel)
        image_copy = self.original_image.copy()
        image_copy = pygame.transform.rotate(image_copy, self.angle_rotate)
        self.angle_rotate += 1
        self.rect = image_copy.get_rect()
        self.rect.center = vec(self.x_start, self.y_start)
        display.blit(image_copy, (self.x_start-int(image_copy.get_width()/2),
                                  self.y_start-int(image_copy.get_height()/2)))
        self.check_for_collision()
        self.check_to_kill()

    def check_for_collision(self):
        global playerGroup
        hits = pygame.sprite.spritecollide(self, playerGroup, False)
        if hits:
            statistics.health -= 1
            self.kill()
            self.hit_sound.play()
            statistics.score -= 2
            player.hitted = True
            player.animate = False
            player.hitted = True

    def check_to_kill(self):
        global disWidth, disHeight, speed, asteroid_group
        if self.x_start <= -10:
            self.kill()
            r = Asteroid(player.pos.x, player.pos.y, speed)
            asteroid_group.add(r)
        if self.x_start >= disWidth+10:
            self.kill()
            r = Asteroid(player.pos.x, player.pos.y, speed)
            asteroid_group.add(r)
        if self.y_start <= -10:
            self.kill()
            r = Asteroid(player.pos.x, player.pos.y, speed)
            asteroid_group.add(r)
        if self.y_start >= disHeight+10:
            self.kill()
            r = Asteroid(player.pos.x, player.pos.y, speed)
            asteroid_group.add(r)


class ManageAsteroids:
    def __init__(self):
        global statistics
        self.killed_asteroids = 0
        self.wave_asteroids = statistics.wave * 2

    def main(self):
        global statistics, asteroid_group, timer, speed, playerBulletsGroup
        if timer >= 180:
            if 0 <= self.wave_asteroids:
                t = Asteroid(player.pos.x, player.pos.y, speed)
                asteroid_group.add(t)
                self.wave_asteroids -= 1
            if self.wave_asteroids <= 0 and len(asteroid_group) == 0:
                self.killed_asteroids = 0
                statistics.wave += 1
                self.wave_asteroids = statistics.wave + 2
                timer = 0
                if statistics.wave >= 10:
                    speed += 0.01


class GameMenu:
    def __init__(self):
        global disWidth, disHeight
        self.font = pygame.font.SysFont('acmefont', 90)
        self.exit_main_menu = 'Exit to main menu'
        self.exit_out = 'Exit to desktop'
        self.back_to_game = 'Resume the game'
        self.play_again = 'Play again'
        self.white = (255, 255, 255)
        self.blue = (24, 255, 213)
        self.x_ex_main_menu = disWidth / 2
        self.y_ex_main_menu = disHeight / 2 - 120
        self.x_ex_desktop = disWidth / 2
        self.y_ex_desktop = disHeight / 2
        self.x_res_game = disWidth / 2
        self.y_res_game = disHeight / 2 - 240
        self.x_play_again = disWidth / 2
        self.y_play_again = disHeight / 2 + 120
        self.exit_main_menu_rendered = self.font.render(self.exit_main_menu, True, self.white)
        self.exit_desktop_rendered = self.font.render(self.exit_out, True, self.white)
        self.resume_game_rendered = self.font.render(self.back_to_game, True, self.white)
        self.play_again_rendered = self.font.render(self.play_again, True, self.white)
        self.width_ex_main_menu = self.exit_main_menu_rendered.get_width()
        self.height_ex_main_menu = self.exit_main_menu_rendered.get_height()
        self.width_ex_desktop = self.exit_desktop_rendered.get_width()
        self.height_ex_desktop = self.exit_desktop_rendered.get_height()
        self.width_res_game = self.resume_game_rendered.get_width()
        self.height_res_game = self.resume_game_rendered.get_height()
        self.width_pl_ag = self.play_again_rendered.get_width()
        self.height_pl_ag = self.play_again_rendered.get_height()
        self.main_menu_real_x = self.x_ex_main_menu - self.width_ex_main_menu / 2
        self.main_menu_real_y = self.y_ex_main_menu - self.height_ex_main_menu / 2
        self.desktop_real_x = self.x_ex_desktop - self.width_ex_desktop / 2
        self.desktop_real_y = self.y_ex_desktop - self.height_ex_desktop / 2
        self.res_game_real_x = self.x_res_game - self.width_res_game / 2
        self.res_game_real_y = self.y_res_game - self.height_res_game / 2
        self.pl_ag_real_x = self.x_play_again - self.width_pl_ag / 2
        self.pl_ag_real_y = self.y_play_again - self.height_pl_ag / 2

    def main(self):
        global display, open_game_menu
        mou_x, mou_y = pygame.mouse.get_pos()
        if self.main_menu_real_x <= mou_x <= self.main_menu_real_x+self.width_ex_main_menu and self.main_menu_real_y <= mou_y <= self.main_menu_real_y+self.height_ex_main_menu:
            self.exit_main_menu_rendered = self.font.render(self.exit_main_menu, True, self.blue)
        else:
            self.exit_main_menu_rendered = self.font.render(self.exit_main_menu, True, self.white)
        if self.desktop_real_x <= mou_x <= self.desktop_real_x+self.width_ex_desktop and self.desktop_real_y <= mou_y <= self.desktop_real_y+self.height_ex_desktop:
            self.exit_desktop_rendered = self.font.render(self.exit_out, True, self.blue)
        else:
            self.exit_desktop_rendered = self.font.render(self.exit_out, True, self.white)
        if self.res_game_real_x <= mou_x <= self.res_game_real_x+self.width_res_game and self.res_game_real_y <= mou_y <= self.res_game_real_y+self.height_res_game:
            self.resume_game_rendered = self.font.render(self.back_to_game, True, self.blue)
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        open_game_menu = False
        else:
            self.resume_game_rendered = self.font.render(self.back_to_game, True, self.white)
        if self.pl_ag_real_x <= mou_x <= self.pl_ag_real_x+self.width_pl_ag and self.pl_ag_real_y <= mou_y <= self.pl_ag_real_y+self.height_pl_ag:
            self.play_again_rendered = self.font.render(self.play_again, True, self.blue)
        else:
            self.play_again_rendered = self.font.render(self.play_again, True, self.white)
        display.blit(self.exit_main_menu_rendered, (self.main_menu_real_x, self.main_menu_real_y))
        display.blit(self.exit_desktop_rendered, (self.desktop_real_x, self.desktop_real_y))
        display.blit(self.resume_game_rendered, (self.res_game_real_x, self.res_game_real_y))
        display.blit(self.play_again_rendered, (self.pl_ag_real_x, self.pl_ag_real_y))

    def menu_without_resume(self):
        global display, open_game_menu, disHeight
        mou_x, mou_y = pygame.mouse.get_pos()
        self.y_play_again = disHeight / 2 - 240
        self.pl_ag_real_y = self.y_play_again - self.height_pl_ag / 2
        if self.main_menu_real_x <= mou_x <= self.main_menu_real_x + self.width_ex_main_menu and self.main_menu_real_y <= mou_y <= self.main_menu_real_y + self.height_ex_main_menu:
            self.exit_main_menu_rendered = self.font.render(self.exit_main_menu, True, self.blue)
        else:
            self.exit_main_menu_rendered = self.font.render(self.exit_main_menu, True, self.white)
        if self.desktop_real_x <= mou_x <= self.desktop_real_x + self.width_ex_desktop and self.desktop_real_y <= mou_y <= self.desktop_real_y + self.height_ex_desktop:
            self.exit_desktop_rendered = self.font.render(self.exit_out, True, self.blue)
        else:
            self.exit_desktop_rendered = self.font.render(self.exit_out, True, self.white)
        if self.pl_ag_real_x <= mou_x <= self.pl_ag_real_x+self.width_pl_ag and self.pl_ag_real_y <= mou_y <= self.pl_ag_real_y+self.height_pl_ag:
            self.play_again_rendered = self.font.render(self.play_again, True, self.blue)
        else:
            self.play_again_rendered = self.font.render(self.play_again, True, self.white)
        display.blit(self.exit_main_menu_rendered, (self.main_menu_real_x, self.main_menu_real_y))
        display.blit(self.exit_desktop_rendered, (self.desktop_real_x, self.desktop_real_y))
        display.blit(self.play_again_rendered, (self.pl_ag_real_x, self.pl_ag_real_y))


class GettingPlayerName:
    def __init__(self):
        global disWidth, disHeight
        self.x = disWidth/2
        self.y = disHeight/2
        self.font = pygame.font.SysFont('agencyfb', 80)
        self.player_name = ''
        self.timer = 0
        self.input = 'Enter your name:'

    def main(self):
        global display, getting_player_name
        if self.player_name == '':
            self.player_name = '|'
        else:
            self.player_name = self.player_name.replace('|', '')
        player_name_rendered = self.font.render(self.player_name, True, (255, 255, 255))
        width = player_name_rendered.get_width()
        height = player_name_rendered.get_height()
        display.blit(player_name_rendered, (self.x-width/2, self.y-height/2))
        input_rendered = self.font.render(self.input, True, (255, 255, 255))
        width = input_rendered.get_width()
        height = input_rendered.get_height()
        display.blit(input_rendered, (self.x-width/2, self.y-100-height/2))


class MainMenu:
    def __init__(self):
        self.font = pygame.font.SysFont('acmefont', 90)
        self.txt_play = 'Play'
        self.txt_leaderboard = 'Leaderboard'
        self.txt_exit_to_desktop = 'Exit to desktop'
        self.white = (255, 255, 255)
        self.blue = (24, 255, 213)
        self.play_rendered = self.font.render(self.txt_play, True, self.white)
        self.play_rect = self.play_rendered.get_rect()

    def main(self):
        global disWidth, disHeight, display
        self.update()
        play_x = disWidth/2
        play_y = disHeight/2
        play_x, play_y = play_x-self.play_rendered.get_width()/2, play_y-self.play_rendered.get_height()/2
        self.play_rect = self.play_rendered.get_rect(x=play_x, y=play_y)
        display.blit(self.play_rendered, (play_x, play_y))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.play_rect.collidepoint(mouse_pos):
            self.play_rendered = self.font.render(self.txt_play, True, self.blue)
        else:
            self.play_rendered = self.font.render(self.txt_play, True, self.white)


# Functions


def print_number(number):
    global display, disWidth
    font = pygame.font.SysFont('agencyfb', 62)
    number_rendered = font.render(str(number), True, (255, 255, 255))
    y = 0
    x = disWidth/2
    width = number_rendered.get_width()
    display.blit(number_rendered, (x-width/2, y))
    return


def print_score(score, wave):
    global display, disWidth, disHeight, timer_for_printing_wave
    font = pygame.font.SysFont('agencyfb', 80)
    score_rendered = font.render('Score: '+str(score), True, (255, 255, 255))
    y = disHeight/2
    x = disWidth/2
    width = score_rendered.get_width()
    height = score_rendered.get_height()
    x = x-width/2
    y = y-height/2
    display.blit(score_rendered, (x, y))
    if timer_for_printing_wave < 60:
        timer_for_printing_wave += 1
    else:
        font = pygame.font.SysFont('agencyfb', 60)
        wave_rendered = font.render('Wave: '+str(wave), True, (255, 255, 255))
        y = disHeight / 2 + 140
        x = disWidth / 2
        width = wave_rendered.get_width()
        height = wave_rendered.get_height()
        x = x - width/2
        y = y - height/2
        display.blit(wave_rendered, (x, y))
    return


def ultimate_power():
    global is_ultimate, timer_for_ultimate, asteroid_group
    is_ultimate = True
    hit_sound = pygame.mixer.Sound('Images\\Bullet_Hit.wav')
    for i in asteroid_group:
        i.kill()
        statistics.mana += 2
        manager.wave_asteroids -= 1
        hit_sound.play()
    return


def print_highscore():
    global highscore, hs_player, statistics, display, disWidth, disHeight, getting_player_name
    font = pygame.font.SysFont('agencyfb', 80)
    if int(highscore) >= statistics.score:
        text_y_d_b_t_h_s = 'You didn\'t beat the highest score:'
        text_hs = str(highscore)
        text_m_b = 'Made by:'
        text_hs_player = hs_player
        y = disHeight/4
        text_y_d_b_t_h_s_rendered = font.render(text_y_d_b_t_h_s, True, (255, 255, 255))
        text_hs_rendered = font.render(text_hs, True, (255, 255, 255))
        text_m_b_rendered = font.render(text_m_b, True, (255, 255, 255))
        text_hs_player_rendered = font.render(text_hs_player, True, (255, 255, 255))
        x = disWidth/2-text_y_d_b_t_h_s_rendered.get_width()/2
        display.blit(text_y_d_b_t_h_s_rendered, (x, y))
        x = disWidth/2-text_hs_rendered.get_width()/2
        display.blit(text_hs_rendered, (x, y+100))
        x = disWidth/2-text_m_b_rendered.get_width()/2
        display.blit(text_m_b_rendered, (x, y+200))
        x = disWidth/2-text_hs_player_rendered.get_width()/2
        display.blit(text_hs_player_rendered, (x, y+300))
    if int(highscore) < statistics.score:
        text_y_b_t_h_s = 'You beat the highest score: {}'.format(highscore)
        text_m_b = 'Made by: {}'.format(hs_player)
        text_t_n_hs_i = 'The new highscore is: {}!'.format(statistics.score)
        y = disHeight/4
        text_y_b_t_h_s_rendered = font.render(text_y_b_t_h_s, True, (255, 255, 255))
        text_m_b_rendered = font.render(text_m_b, True, (255, 255, 255))
        text_t_n_hs_i_rendered = font.render(text_t_n_hs_i, True, (255, 255, 255))
        x = disWidth/2-text_y_b_t_h_s_rendered.get_width()/2
        display.blit(text_y_b_t_h_s_rendered, (x, y))
        x = disWidth/2-text_m_b_rendered.get_width()/2
        display.blit(text_m_b_rendered, (x, y+100))
        x = disWidth/2-text_t_n_hs_i_rendered.get_width()/2
        display.blit(text_t_n_hs_i_rendered, (x, y+200))
        getting_player_name = True


# Main loop
game_for_loop = False
number = 1
while True:

    # Other
    player = Player(disWidth // 2, disHeight // 2)
    cursor = Cursor()
    statistics = Statistics()
    game_menu = GameMenu()
    asteroid_group = pygame.sprite.Group()
    manager = ManageAsteroids()
    player_name = GettingPlayerName()
    main_menu = MainMenu()
    playerBulletsGroup = pygame.sprite.Group()
    playerGroup = pygame.sprite.Group()
    playerGroup.add(player)
    player_shoot_sound = pygame.mixer.Sound('Images\\Player_Shoot.wav')
    menu_sound = pygame.mixer.Sound('Images\\Menu_Sound.wav')
    timer = 0
    speed = 5
    timer_for_printing_wave = 0
    timer_for_game_menu = 0
    timer_for_ultimate = 0
    is_ultimate = False
    open_game_menu = False
    with open('highscore.txt', 'r') as file:
        line = file.read()
    line = line.split(',')
    highscore = line[0]
    hs_player = line[1]
    getting_player_name = False
    end_menu = False
    while game_for_loop and number == 0:
        if not is_ultimate:
            display.fill((0, 0, 0))
        elif is_ultimate and timer_for_ultimate <= 10:
            timer_for_ultimate += 1
            display.fill((125, 255, 86))
        else:
            is_ultimate = False
            timer_for_ultimate = 0
            display.fill((0, 0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) and not open_game_menu and player in playerGroup:
                end_menu = True
                open_game_menu = True
                cursor.game = False
            if not open_game_menu and player in playerGroup:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if player in playerGroup:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            bullet = PlayerBullet(player.pos.x, player.pos.y, mouse_x, mouse_y)
                            playerBulletsGroup.add(bullet)
                            player.animate = False
                            player_shoot_sound.play()
                    if event.button == 3:
                        if player in playerGroup:
                            if statistics.mana >= 100:
                                statistics.mana = 0
                                ultimate_power()
                if event.type == pygame.KEYDOWN:
                    if statistics.mana >= 100:
                        if event.key == pygame.K_e:
                            statistics.mana = 0
                            statistics.health += 1
            if open_game_menu and player in playerGroup:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        m_x, m_y = pygame.mouse.get_pos()
                        if game_menu.res_game_real_x <= m_x <= game_menu.res_game_real_x + game_menu.width_res_game and game_menu.res_game_real_y <= m_y <= game_menu.res_game_real_y + game_menu.height_res_game:
                            open_game_menu = False
                            cursor.game = True
                            menu_sound.play()
                            end_menu = False
                        if game_menu.desktop_real_x <= m_x <= game_menu.desktop_real_x + game_menu.width_ex_desktop and game_menu.desktop_real_y <= m_y <= game_menu.desktop_real_y + game_menu.height_ex_desktop:
                            menu_sound.play()
                            time.sleep(0.08)
                            pygame.quit()
                            sys.exit()
                        if game_menu.pl_ag_real_x <= m_x <= game_menu.pl_ag_real_x+game_menu.width_pl_ag and game_menu.pl_ag_real_y <= m_y <= game_menu.pl_ag_real_y+game_menu.height_pl_ag:
                            menu_sound.play()
                            time.sleep(0.08)
                            game_for_loop = True
                            number = 1
                            break
                        if game_menu.main_menu_real_x <= m_x <= game_menu.main_menu_real_x+game_menu.width_ex_main_menu and game_menu.main_menu_real_y <= m_y <= game_menu.main_menu_real_y+game_menu.height_ex_main_menu:
                            menu_sound.play()
                            time.sleep(0.08)
                            game_for_loop = False
                            number = 1
                            break
            if not open_game_menu and player not in playerGroup and timer_for_game_menu >= 420 and not getting_player_name:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        m_x, m_y = pygame.mouse.get_pos()
                        if game_menu.desktop_real_x <= m_x <= game_menu.desktop_real_x + game_menu.width_ex_desktop and game_menu.desktop_real_y <= m_y <= game_menu.desktop_real_y + game_menu.height_ex_desktop:
                            menu_sound.play()
                            time.sleep(0.08)
                            pygame.quit()
                            sys.exit()
                        if game_menu.pl_ag_real_x <= m_x <= game_menu.pl_ag_real_x+game_menu.width_pl_ag and game_menu.pl_ag_real_y <= m_y <= game_menu.pl_ag_real_y+game_menu.height_pl_ag:
                            menu_sound.play()
                            time.sleep(0.08)
                            game_for_loop = True
                            number = 1
                            break
                        if game_menu.main_menu_real_x <= m_x <= game_menu.main_menu_real_x+game_menu.width_ex_main_menu and game_menu.main_menu_real_y <= m_y <= game_menu.main_menu_real_y+game_menu.height_ex_main_menu:
                            menu_sound.play()
                            time.sleep(0.08)
                            game_for_loop = False
                            number = 1
                            break
            if not open_game_menu and player not in playerGroup and timer_for_game_menu >= 420 and getting_player_name and not end_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        time.sleep(0.08)
                        getting_player_name = False
                        with open('highscore.txt', 'w') as file:
                            line = str(statistics.score)+','+player_name.player_name
                            file.write(line)
                    elif event.key == pygame.K_BACKSPACE:
                        player_name.player_name = player_name.player_name[0:-1]
                    else:
                        player_name.player_name += event.unicode

        # Including code
        if not open_game_menu:
            if player in playerGroup:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    player.acc.x -= 1
                if keys[pygame.K_d]:
                    player.acc.x += 1
                if keys[pygame.K_s]:
                    player.acc.y += 1
                if keys[pygame.K_w]:
                    player.acc.y -= 1
            if statistics.health <= 0:
                player.kill()
            if 0 <= timer < 60:
                print_number(3)
                timer += 1
            if 60 <= timer < 120:
                print_number(2)
                timer += 1
            if 120 <= timer < 180:
                print_number(1)
                timer += 1
            if player in playerGroup:
                manager.main()
        if player not in playerGroup and timer_for_game_menu < 180:
            cursor.game = False
            print_score(statistics.score, statistics.wave)
            timer_for_game_menu += 1
        elif player not in playerGroup and 180 <= timer_for_game_menu < 420:
            cursor.game = False
            print_highscore()
            timer_for_game_menu += 1
        if timer_for_game_menu >= 420 and getting_player_name:
            if not end_menu:
                player_name.main()
            cursor.game = False
        elif timer_for_game_menu >= 420 and not getting_player_name:
            game_menu.menu_without_resume()
            cursor.game = False

        # Updating images
        if not open_game_menu:
            if player in playerGroup:
                player.main()
                for a in asteroid_group:
                    a.main()
                for b in playerBulletsGroup:
                    b.main()
                statistics.render()
        cursor.main()
        if open_game_menu and player in playerGroup:
            game_menu.main()
            cursor.game = False

        # Updating display
        pygame.display.update()
        clock.tick(60)
    while not game_for_loop and number == 1:
        display.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                if main_menu.play_rect.collidepoint(mouse_position):
                    game_for_loop = True
                    number = 0
                    menu_sound.play()
                    time.sleep(0.08)
                    break
        main_menu.main()
        clock.tick(60)
        pygame.display.update()
    if game_for_loop and number == 1:
        number = 0
