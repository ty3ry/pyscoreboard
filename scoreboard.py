
import pygame as pg
import os
import platform
import thread
import time
from datetime import datetime
import pylirc
import random

# full screen option
OPS_FULLSCREEN = True
tick_c = 0



# constant definition
# color definition
LOGIN_COLOR = (120, 104, 192)
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

# game status
GAME_STATUS_PAUSE = 0
GAME_STATUS_PLAY = 1
GAME_STATUS_STOP = 2
GAME_STATUS_FINISH = 3
GAME_STATUS_IDLE = 4

# score limit
GAME_SCORE_LIMIT = 100
GAME_POINT_VAL = 11
GAME_LAST_ONE = (GAME_POINT_VAL-1)

# game play state
GAME_PLAY_STATE_IDLE = 0
#GAME_PLAY_STATE_RUNNING = 1
GAME_PLAY_STATE_RED_WIN = 1
GAME_PLAY_STATE_BLUE_WIN = 2
GAME_PLAY_STATE_DEUCE = 3
# screen size
SCREEN_SIZE = (0, 0)
# end of constant definition  #


pg.init() 
pg.mouse.set_visible(False)



class Scoreboard(object):
    def __init__(self):
        # py lirc blocking control
        self.blocking = 0
        # set font score red
        self.red_score_template = pg.font.SysFont('arial', 320)
        self.red_score_template.set_bold(True)

        # set font score blue
        self.blue_score_template = pg.font.SysFont('arial', 320)
        self.blue_score_template.set_bold(True)

        # set font game time
        self.game_time_template = pg.font.SysFont('comicsansms', 80)
        self.game_time_template.set_bold(True)

        # set font game status
        self.game_status_template = pg.font.SysFont('comicsansms', 60)
        self.game_status_template.set_bold(False)

        # set font score (universal)
        self.score_template = pg.font.SysFont('comicsansms', 60)
        self.score_template.set_bold(False)

        # Game set number
        self.game_set_template = pg.font.SysFont('comicsansms', 100)
        self.game_set_template.set_bold(False)

        self.red_score = 0
        self.blue_score = 0
        self.game_time = 0
        self.serv_pos = 0
        self.game_status = 0
        self.str_game_status = ""
        self.update_score = 0
        self.game_state_play = 0
        self.power_status = 0        # 0 : power off     1 : power on
        self.is_game_done = 0
        self.ser_pos_count = 0
        self.menit = 0
        self.detik = 0

        self.score_data = {
            "red" : 0,
            "blue" : 0,
            "current_set" : 1,
            "set1_red" : 0,
            "set1_blue" : 0,
            "set2_red" : 0,
            "set2_blue" : 0,
        }

        if(OPS_FULLSCREEN == True) :
            self.screen = pg.display.set_mode((0,0))
        else:
            SCREEN_SIZE = (480,320)
            self.screen = pg.display.set_mode(SCREEN_SIZE)  

        self.SCREEN_W = self.screen.get_rect().width
        self.SCREEN_H = self.screen.get_rect().height

        self.poff_image = pg.image.load("resource/90.png")
        self.poff_image = pg.transform.scale(self.poff_image, (self.SCREEN_W, self.SCREEN_H))

        self.clock = pg.time.Clock()

    def update_background(self):
        self.screen.fill(BLUE)
        pg.draw.rect(self.screen, RED, (0,0,self.SCREEN_W/2, self.SCREEN_H))
        pg.draw.rect(self.screen, BLACK, (0, self.SCREEN_H-100, self.SCREEN_W, 100))
        pg.draw.rect(self.screen, GRAY, (0, self.SCREEN_H-100, self.SCREEN_W, 100), 3)

    def update_red_score(self, surface, msg):
        red_score_label = self.red_score_template.render(msg, 1, WHITE)
        x = (self.SCREEN_W/2 - red_score_label.get_rect().w) /2
        surface.blit(red_score_label, (x , 100))

    def update_blue_score(self, surface, msg):
        blue_score_label = self.blue_score_template.render(msg, 1, WHITE)
        x = (self.SCREEN_W - (self.SCREEN_W/4) - blue_score_label.get_rect().w/2)
        surface.blit(blue_score_label, (x , 100))

    def draw_frame_game_time(self, surface, t):
        w = 300
        h = 100
        x = (self.SCREEN_W/2) - (w/2)
        y = (0)
        pg.draw.rect(self.screen, WHITE, (x,y,w,h))
        
        game_time_label = self.game_time_template.render(t, 1 , BLACK)
        ax = (self.SCREEN_W/2) - game_time_label.get_width()/2
        ay = 20
        surface.blit(game_time_label, (ax,ay))

    def draw_game_status(self, surface, status) :
        ax = (self.SCREEN_W)
        ay = (self.SCREEN_H - 80)
        game_status_label = self.game_status_template.render(status, 1 , WHITE)
        surface.blit(game_status_label, (ax - game_status_label.get_width() - 20, ay))

    def draw_score_set(self, set):
        xpos = 20
        x,y = (120, self.SCREEN_H-100+2)
        w,h = (100, (100/2)-2)

        if set==1:
            self.score_data["set1_red"] = self.red_score
            self.score_data["set1_blue"] = self.blue_score
        elif set==2:
            self.score_data["set2_red"] = self.red_score
            self.score_data["set2_blue"] = self.blue_score
        i = 1
        for i in range(set):
            # set 1
            # red score
            print(i)
            x = (x) + w
            y = (self.SCREEN_H-(100/2))
            #score_label = 0
            if i == 0:
                score_label = self.score_template.render(str(self.score_data["set1_red"]), 1 , WHITE)
                self.screen.blit(score_label, (x , y))
            elif i == 1:
                score_label = self.score_template.render(str(self.score_data["set2_red"]), 1 , WHITE)
                self.screen.blit(score_label, (x , y))

            # blue score
            x = (x)
            y = (self.SCREEN_H-(100/2) - 45)
            if i == 0:
                score_label = self.score_template.render(str(self.score_data["set1_blue"]), 1 , WHITE)
                self.screen.blit(score_label, (x , y))
            elif i == 1:
                score_label = self.score_template.render(str(self.score_data["set2_blue"]), 1 , WHITE)
                self.screen.blit(score_label, (x , y))
            
        # frame set 1
        ax,ay = (x-40, self.SCREEN_H-100)
        aw,ah = (100,100)
        pg.draw.rect(self.screen, YELLOW, (ax,ay,aw,ah), 4)          # red region

        # game set number
        x = (ax + 150)
        y = (self.SCREEN_H-(100/2) - 40)
        game_set_label = self.game_set_template.render(str(set), 1 , RED)
        self.screen.blit(game_set_label, (x , y))
            

    def draw_frame_match_set(self, serpos, set, blue_score_set, red_score_set):
        xpos = 0
        x,y = (xpos,self.SCREEN_H-100)
        w,h = ((self.SCREEN_W/2)-xpos,100)
        pg.draw.rect(self.screen, YELLOW, (x,y,w, h), -2)     # border

        x,y = (xpos+2, self.SCREEN_H-100+2)
        w,h = (180-2, (h/2)-2)
        pg.draw.rect(self.screen, BLUE, (x,y,w,h))           # blue region
        x,y = (x+2, self.SCREEN_H-(100/2)+2)
        w,h = (w-2,h-2)
        pg.draw.rect(self.screen, RED, (x,y,w,h))          # red region

        # service position
        rad = 10        # circle radius
        if serpos == 0:
            pg.draw.circle(self.screen, WHITE, (40, self.SCREEN_H-30), rad)
        else :
            pg.draw.circle(self.screen, WHITE, (40, self.SCREEN_H-70), rad)
        
        # game set score -- blue
        x = 120
        y = (self.SCREEN_H-(100/2))
        score_label = self.score_template.render(str(blue_score_set), 1 , YELLOW)
        self.screen.blit(score_label, (x , y))

        # red
        x = (x)
        y = (self.SCREEN_H-(100/2) - 45)
        score_label = self.score_template.render(str(red_score_set), 1 , YELLOW)

        self.screen.blit(score_label, (x , y))
        self.draw_score_set(set)
        
        
    def update_service_pos(self, screen, pos):
        rad = 22
        if pos == False:
            pg.draw.circle(self.screen, WHITE, (self.SCREEN_W/4, self.SCREEN_H-200), rad)
        else :
            pg.draw.circle(self.screen, WHITE, (self.SCREEN_W - (self.SCREEN_W/4), self.SCREEN_H-200), rad)


    def generate_tick(self):
        global tick_c
        status = False

        x=datetime.today()
        y=x.replace(day=x.day+1, hour=3, minute=1, second=0, microsecond=0)
        delta_t=y-x
        secs=delta_t.seconds+1

        second = (secs % 60)
        minut = (secs / 60) % 60
        hour = (secs / 3600)

        if tick_c != second:
            # print ("Time is %s:%s:%s" % (hour, minut, second))
            tick_c = second
            status = True
        else :
            status = False
        
        return (status)

    # set picture on power off
    def picture_poweroff(self, surface, image):
        surface.blit(image, image.get_rect())

    def display_refresh(self,power_state):
        if not power_state :
            self.update_background()
            self.update_red_score(self.screen, str(self.red_score))
            self.update_blue_score(self.screen, str(self.blue_score))
            self.draw_frame_game_time(self.screen, str(self.menit) + ":" + str(self.detik))
            self.update_service_pos(self.screen, self.serv_pos)
            self.draw_game_status(self.screen, self.str_game_status)
            self.draw_frame_match_set(self.serv_pos, self.score_data["current_set"],self.score_data["blue"], self.score_data["red"])
        else:
            self.picture_poweroff(self.screen, self.poff_image)
        
        pg.display.flip()
        self.clock.tick(60)

    def run(self):
        running = 1
        # main looping    
        while running:

            if(pylirc.init("sb", "pylirc.conf", self.blocking)):
                code = {"config" : ""}
                while (code["config"] != "quit"):
                    
                    # display refresh
                    self.display_refresh(power_state=self.power_status)

                    if self.game_status == GAME_STATUS_PLAY:
                        self.str_game_status = "Game : Play"
                        if self.generate_tick() == True :
                            self.detik = self.detik + 1
                            if(self.detik > 59):
                                self.detik = 0
                                self.menit = self.menit + 1
                                if self.menit > 59:
                                    self.menit = 0

                        if self.update_score == 1:
                            # change service pos
                            if self.game_state_play == GAME_PLAY_STATE_DEUCE:
                                if((self.blue_score + self.red_score) % 1 == 0) :
                                    self.serv_pos = not self.serv_pos
                                    print "ganti service..."
                                    self.update_score = 0
                            else:
                                if((self.blue_score + self.red_score) % 2 == 0) :
                                    self.serv_pos = not self.serv_pos
                                    print "ganti service..."
                                    self.update_score = 0
                                
                    elif self.game_status == GAME_STATUS_STOP:
                        self.str_game_status = "Game : Stop"
                        # reset data
                        self.detik = 0
                        self.menit = 0
                        self.blue_score = 0
                        self.red_score = 0
                        self.is_game_done = False
                        self.update_score = 0

                    elif self.game_status == GAME_STATUS_PAUSE:
                        self.str_game_status = "Game : Pause"
                    elif self.game_status == GAME_STATUS_FINISH:
                        if self.game_state_play == GAME_PLAY_STATE_BLUE_WIN:
                            self.str_game_status = "Game : Finish (Blue win)"
                        elif self.game_state_play == GAME_PLAY_STATE_RED_WIN:
                            self.str_game_status = "Game : Finish (Red Win)"
                

                    s = pylirc.nextcode(1)
                    while(s):
                        for (code) in s :
                            print("Command: %s, Repeat: %d" % (code["config"], code["repeat"]))

                            if self.is_game_done==False:
                                if(code["config"] == "one"):
                                    if self.game_status==GAME_STATUS_PLAY :
                                        if self.red_score < GAME_SCORE_LIMIT:
                                            self.red_score = self.red_score + 1
                                            self.update_score = 1
                                elif(code["config"] == "four"):
                                    if self.game_status==GAME_STATUS_PLAY:
                                        if self.red_score > 0 :
                                            self.red_score = self.red_score - 1
                                            self.update_score = 1
                                elif(code["config"] == "three"):
                                    if self.game_status==GAME_STATUS_PLAY :
                                        if self.blue_score < GAME_SCORE_LIMIT :
                                            self.blue_score = self.blue_score + 1      
                                            self.update_score = 1 
                                elif(code["config"] == "six"):
                                    if self.game_status==GAME_STATUS_PLAY :
                                        if self.blue_score > 0 :
                                            self.blue_score = self.blue_score - 1
                                            self.update_score = 1
                            

                            if self.is_game_done ==False:
                                # change service position
                                # valid on pause or stop mode
                                if(code["config"] == "key_left" and self.game_status != GAME_STATUS_PLAY):
                                    self.serv_pos = False
                                elif(code["config"] == "key_right" and self.game_status != GAME_STATUS_PLAY):
                                    self.serv_pos = True

                            # game status control
                            if(code["config"] == "key_play"):
                                self.game_status = GAME_STATUS_PLAY
                                if self.game_state_play == GAME_PLAY_STATE_RED_WIN or self.game_state_play == GAME_PLAY_STATE_BLUE_WIN:
                                    if self.score_data["current_set"] < 5 :
                                        self.score_data["current_set"] = self.score_data["current_set"] + 1
                                        self.blue_score = 0
                                        self.red_score = 0
                                    #print("set : %d " % (self.score_data["current_set"]))
                            elif(code["config"] == "key_pause"):
                                self.game_status = GAME_STATUS_PAUSE
                            elif(code["config"] == "key_stop"):
                                self.game_status = GAME_STATUS_STOP
                            elif(code["config"] == "key_power"):
                                print "key power pressed"
                                self.power_status = not self.power_status     # toggle state
                            else :
                                pass
                            
                            # winner calculate
                            if self.game_status == GAME_STATUS_PLAY:
                                if (self.blue_score >= GAME_POINT_VAL and (self.blue_score - self.red_score) >= 2):
                                    print "game state : blue win"
                                    #str_game_status = "Blue Win"
                                    self.game_state_play = GAME_PLAY_STATE_BLUE_WIN
                                    self.game_status = GAME_STATUS_FINISH
                                    self.is_game_done = True
                                elif (self.red_score >= GAME_POINT_VAL and (self.red_score-self.blue_score) >= 2) :
                                    print "game state : red win"
                                    #str_game_status = "Red Win"
                                    self.game_state_play = GAME_PLAY_STATE_RED_WIN
                                    self.game_status = GAME_STATUS_FINISH
                                    self.is_game_done = True
                                elif (self.red_score >= GAME_LAST_ONE and self.blue_score >= GAME_LAST_ONE and self.red_score == self.blue_score) :
                                    print "game state : deuce"
                                    self.game_state_play = GAME_PLAY_STATE_DEUCE
                                else :
                                    pass

                            if (not self.blocking):
                                s = pylirc.nextcode(1)
                            else:
                                s = []

if __name__ == "__main__":
    scoreboard = Scoreboard()
    scoreboard.run()
    
    