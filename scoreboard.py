import pygame as pg
import os
import platform
import thread
import time
from datetime import datetime

import pylirc

# full screen option
OPS_FULLSCREEN = True
tick_c = 0

# py lirc blocking control
blocking = 0

#############################################
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

# end of constant definition  #


# screen size
SCREEN_SIZE = (0, 0)

if(OPS_FULLSCREEN == True) :
    screen = pg.display.set_mode((0,0))
else:
    SCREEN_SIZE = (480,320)
    screen = pg.display.set_mode(SCREEN_SIZE)  
        
SCREEN_W = screen.get_rect().width
SCREEN_H = screen.get_rect().height


pg.init() 
pg.mouse.set_visible(False)
clock = pg.time.Clock()
# print screen size
print("screen size : %s " % (screen.get_rect()))

red_score = 0
blue_score = 0
game_time = 0
serv_pos = 0
game_status = 1
str_game_status = ""
update_score = 0
game_state_play = 0
power_status = 0        # 0 : power off     1 : power on
is_game_done = 0
ser_pos_count = 0


'''
data = {
    "score" : 1,
    ""
}
'''

# variable for time
menit = 0
detik = 0

# set font score red
red_score_template = pg.font.SysFont('arial', 320)
red_score_template.set_bold(True)

# set font score blue
blue_score_template = pg.font.SysFont('arial', 320)
blue_score_template.set_bold(True)

# set font game time
game_time_template = pg.font.SysFont('comicsansms', 80)
game_time_template.set_bold(True)

# set font game status
game_status_template = pg.font.SysFont('comicsansms', 60)
game_status_template.set_bold(False)

# load picture
poff_image = pg.image.load("resource/89.jpg")

def update_background():
    screen.fill(BLUE)
    pg.draw.rect(screen, RED, (0,0,SCREEN_W/2, SCREEN_H))
    pg.draw.rect(screen, BLACK, (0, SCREEN_H-100, SCREEN_W, 100))
    

def update_red_score(surface, msg):
    red_score_label = red_score_template.render(msg, 1, WHITE)
    x = (SCREEN_W/2 - red_score_label.get_rect().w) /2
    surface.blit(red_score_label, (x , 100))


def update_blue_score(surface, msg):
    blue_score_label = blue_score_template.render(msg, 1, WHITE)
    x = (SCREEN_W - (SCREEN_W/4) - blue_score_label.get_rect().w/2)
    surface.blit(blue_score_label, (x , 100))

def draw_frame_game_time(surface, t):
    w = 300
    h = 100
    x = (SCREEN_W/2) - (w/2)
    y = (0)
    pg.draw.rect(screen, WHITE, (x,y,w,h))
    
    game_time_label = game_time_template.render(t, 1 , BLACK)
    ax = (SCREEN_W/2) - game_time_label.get_width()/2
    ay = 20
    surface.blit(game_time_label, (ax,ay))

def draw_game_status(surface, status) :
    ax = 10
    ay = (SCREEN_H - 80)
    game_status_label = game_status_template.render(status, 1 , WHITE)
    surface.blit(game_status_label, (ax, ay))

def update_service_pos(screen, pos):
    rad = 22

    if pos == False:
        pg.draw.circle(screen, WHITE, (SCREEN_W/4, SCREEN_H-200), rad)
    else :
        pg.draw.circle(screen, WHITE, (SCREEN_W - (SCREEN_W/4), SCREEN_H-200), rad)

def handleEvent():
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            return event.key

def generate_tick():
    global tick_c
    status = False

    x=datetime.today()
    y=x.replace(day=x.day+1, hour=3, minute=1, second=0, microsecond=0)
    delta_t=y-x
    secs=delta_t.seconds+1

    second = (secs % 60)
    minut = (secs / 60) % 60
    hour = (secs / 3600)
    # print ("Seconds: %s " % (second))
    # print ("Minute: %s " % (minut))
    # print ("Hour: %s" % (hour))

    if tick_c != second:
        # print ("Time is %s:%s:%s" % (hour, minut, second))
        tick_c = second
        status = True
    else :
        status = False
    
    return (status)

# set picture on power off
def picture_poweroff(surface, image):
    #surface.blit(image, (0, 0))
    surface.blit(image, image.get_rect())
    pass

def display_refresh(power_state):
    if power_state :
        update_background()
        update_red_score(screen, str(red_score))
        update_blue_score(screen, str(blue_score))
        draw_frame_game_time(screen, str(menit) + ":" + str(detik))
        update_service_pos(screen, serv_pos)
        draw_game_status(screen, str_game_status)
    else:
        picture_poweroff(screen, poff_image)
        pass
    
    pg.display.flip()
    clock.tick(60)

def winner_process():
    # winner calculate
    if (blue_score >= GAME_POINT_VAL and (blue_score - red_score) >= 2):
        print "game state : blue win"
        str_game_status = "Blue Win"
        game_state_play = GAME_PLAY_STATE_BLUE_WIN
        game_status = GAME_STATUS_FINISH
        is_game_done = True
    elif (red_score >= GAME_POINT_VAL and (red_score-blue_score) >= 2) :
        print "game state : red win"
        str_game_status = "Red Win"
        game_state_play = GAME_PLAY_STATE_RED_WIN
        game_status = GAME_STATUS_FINISH
        is_game_done = True
    elif (red_score >= GAME_LAST_ONE and blue_score >= GAME_LAST_ONE and red_score == blue_score) :
        print "game state : deuce"
        game_state_play = GAME_PLAY_STATE_DEUCE
    else :
        #game_state_play = GAME_PLAY_STATE_RUNNING
        #print "game state : running"
        pass


running = 1
# main looping    
while running:
    event = handleEvent()

    if event == pg.K_ESCAPE:
        running = False

    if(pylirc.init("sb", "pylirc.conf", blocking)):
        code = {"config" : ""}
        while (code["config"] != "quit"):
            
            # display refresh
            display_refresh(power_state=power_status)

             

            if game_status == GAME_STATUS_PLAY:
                str_game_status = "Game : Play"
                if generate_tick() == True :
                    detik = detik + 1
                    if(detik > 59):
                        detik = 0
                        menit = menit + 1
                        if menit > 59:
                            menit = 0

                if update_score == 1:
                    # change service pos
                    if game_state_play == GAME_PLAY_STATE_DEUCE:
                        if((blue_score + red_score) % 1 == 0) :
                            serv_pos = not serv_pos
                            print "ganti service..."
                            update_score = 0
                    else:
                        if((blue_score + red_score) % 2 == 0) :
                            serv_pos = not serv_pos
                            print "ganti service..."
                            update_score = 0
                        
            elif game_status == GAME_STATUS_STOP:
                str_game_status = "Game : Stop"
                # reset data
                detik = 0
                menit = 0
                blue_score = 0
                red_score = 0
                is_game_done = False

            elif game_status == GAME_STATUS_PAUSE:
                str_game_status = "Game : Pause"
            elif game_status == GAME_STATUS_FINISH:
                if game_state_play == GAME_PLAY_STATE_BLUE_WIN:
                    str_game_status = "Game : Finish (Blue win)"
                elif game_state_play == GAME_PLAY_STATE_RED_WIN:
                    str_game_status = "Game : Finish (Red Win)"
        

            s = pylirc.nextcode(1)
            while(s):
                for (code) in s :
                    print("Command: %s, Repeat: %d" % (code["config"], code["repeat"]))

                    if is_game_done==False:
                        if(code["config"] == "one"):
                            if game_status==GAME_STATUS_PLAY :
                                if red_score < GAME_SCORE_LIMIT:
                                    red_score = red_score + 1
                                    update_score = 1
                        elif(code["config"] == "four"):
                            if game_status==GAME_STATUS_PLAY:
                                if red_score > 0 :
                                    red_score = red_score - 1
                                    update_score = 1
                        elif(code["config"] == "three"):
                            if game_status==GAME_STATUS_PLAY :
                                if blue_score < GAME_SCORE_LIMIT :
                                    blue_score = blue_score + 1      
                                    update_score = 1 
                        elif(code["config"] == "six"):
                            if game_status==GAME_STATUS_PLAY :
                                if blue_score > 0 :
                                    blue_score = blue_score - 1
                                    update_score = 1
                    

                    if is_game_done ==False:
                        # change service position
                        # valid on pause or stop mode
                        if(code["config"] == "key_left" and game_status != GAME_STATUS_PLAY):
                            serv_pos = False
                        elif(code["config"] == "key_right" and game_status != GAME_STATUS_PLAY):
                            serv_pos = True

                    # game status control
                    if(code["config"] == "key_play"):
                        game_status = GAME_STATUS_PLAY
                    elif(code["config"] == "key_pause"):
                        game_status = GAME_STATUS_PAUSE
                    elif(code["config"] == "key_stop"):
                        game_status = GAME_STATUS_STOP
                    elif(code["config"] == "key_power"):
                        print "key power pressed"
                        power_status = not power_status     # toggle state
                    else :
                        pass
                    
                    # winner calculate
                    if game_status == GAME_STATUS_PLAY:
                        if (blue_score >= GAME_POINT_VAL and (blue_score - red_score) >= 2):
                            print "game state : blue win"
                            #str_game_status = "Blue Win"
                            game_state_play = GAME_PLAY_STATE_BLUE_WIN
                            game_status = GAME_STATUS_FINISH
                            is_game_done = True
                        elif (red_score >= GAME_POINT_VAL and (red_score-blue_score) >= 2) :
                            print "game state : red win"
                            #str_game_status = "Red Win"
                            game_state_play = GAME_PLAY_STATE_RED_WIN
                            game_status = GAME_STATUS_FINISH
                            is_game_done = True
                        elif (red_score >= GAME_LAST_ONE and blue_score >= GAME_LAST_ONE and red_score == blue_score) :
                            print "game state : deuce"
                            game_state_play = GAME_PLAY_STATE_DEUCE
                        else :
                            #game_state_play = GAME_PLAY_STATE_RUNNING
                            #print "game state : running"
                            pass

                    if (not blocking):
                        s = pylirc.nextcode(1)
                    else:
                        s = []

    #pg.display.flip()
    #clock.tick(60)
    
    