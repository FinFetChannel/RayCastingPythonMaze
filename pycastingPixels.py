import numpy as np
from time import time
from numba import njit
import pygame as pg
from pygame.locals import (K_UP, K_DOWN,K_LEFT,K_RIGHT,K_ESCAPE,KEYDOWN,QUIT)



def main():

    size = 15
    posx, posy, rot = (1, np.random.randint(1, size -1), 1) # player pos
    bg = np.linspace(0, 1, 150) #background gradient
    mapc, maph, mapr, ex, ey = maze_generator(posx, posy, size)# map, exit
    width = 150
    mod = width/60
    height = int(width*0.75)
    bench=[]
    
    running = True
    pg.init()
    font = pg.font.SysFont("Arial", 18)
    pg.mouse.set_visible(False)
    pg.mouse.set_pos([320, 240])
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    half_h = int(height/2-1)
    sky = np.asarray([np.linspace(0,.3,half_h),np.linspace(0,.7,half_h),np.linspace(0,1,half_h)]).T
    floor = np.asarray([np.linspace(0,1,height - half_h),np.linspace(0,1,height - half_h),np.linspace(0,1,height - half_h)]).T
    while running:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False


##    while True: #main game loop
        start = time()
        pixels = np.ones([height, width, 3])
        for i in range(width): #vision loop
            rot_i = rot + np.deg2rad(i/mod - 30)
            pixels[0:half_h,i] = sky*(0.7 + np.sin((rot_i+np.pi/2)/2)**2/3)
            pixels[half_h:,i] = floor*(0.5 + np.sin((rot_i-np.pi/2)/2)**2/2)
            x, y = (posx, posy)
            sin, cos = (0.02*np.sin(rot_i), 0.02*np.cos(rot_i))
            n, half = 0, None
            c, h, x, y, n, half, ty, tc = caster(x, y, i/mod, ex, ey, maph, mapc, sin, cos, n, half)
            if mapr[int(x)][int(y)] == 1:
                 pixels, ty, tc = reflection(x, y, i, ex, ey, maph, mapc, sin, cos, n, c, h, half, pixels, ty, tc, height)
##            pixels = draw_tiles(i, ty, tc, height, pixels)
            else:
                pixels[int((height - h*height)/2):int((height+h*height)/2),i] = c
                if half !=  None:
                    pixels[int(height/2):int((height+half[0]*height)/2),i] = half[1]
            
        # player's movement
        pressed_keys = pg.key.get_pressed()
        
        if (int(posx) == ex and int(posy) == ey):
            break
        rot = rotation(rot, pg.mouse.get_pos())
        pg.mouse.set_pos([320, 240])
        posx, posy, rot = movement(pressed_keys,posx, posy, rot, maph, clock.tick()/500)
        surf = pg.surfarray.make_surface(np.rot90(pixels*255).astype('uint8'))
        surf = pg.transform.scale(surf, (640, 480))
        screen.blit(surf, (0, 0))
        fps = font.render(str(int(clock.get_fps())), 1, pg.Color("coral"))
        screen.blit(fps,(10,0))
        pg.display.update()




        # Flip the display

##        pg.display.flip()
        bench.append(1/(time()-start+1e-16))

##    plt.close()
    pg.quit()
    print(np.mean(bench))
    
def maze_generator(x, y, size):
    mapc = np.random.uniform(0,1, (size,size,3)) 
    mapr = np.random.choice([0, 0, 0, 0, 1], (size,size))
    maph = np.random.choice([0, 0, 0, 0, .5, 1], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)

    mapc[x][y], maph[x][y], mapr[x][y] = (0, 0, 0)
    count = 0 
    while 1:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx = testx + np.random.choice([-1, 1])
        else:
            testy = testy + np.random.choice([-1, 1])
        if testx > 0 and testx < size -1 and testy > 0 and testy < size -1:
            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                mapc[x][y], maph[x][y], mapr[x][y] = (0, 0, 0)
                if x == size-2:
                    ex, ey = (x, y)
                    break
            else:
                count = count+1
    return np.asarray(mapc), np.asarray(maph), np.asarray(mapr), ex, ey

def rotation(rot, position): # for 1080p screen
    delta = (position[0] - 320)
    rot = rot + 4*np.pi*(0.5-delta/6400)
    return(rot)

def on_press(key_new):
    global key
    key = key_new

def movement(pressed_keys,posx, posy, rot, maph, et):
    x, y = (posx, posy)
    if pressed_keys[K_UP] or pressed_keys[ord('w')]:
        x, y = (x + et*np.cos(rot), y + et*np.sin(rot))
    if pressed_keys[K_DOWN] or pressed_keys[ord('s')]:
        x, y = (x - et*np.cos(rot), y - et*np.sin(rot))
    if pressed_keys[K_LEFT] or pressed_keys[ord('a')]:
        x, y = (x - et*np.sin(rot), y + et*np.cos(rot))
    if pressed_keys[K_RIGHT] or pressed_keys[ord('d')]:
        x, y = (x + et*np.sin(rot), y - et*np.cos(rot))
    if maph[int(x)][int(y)] == 0:
        posx, posy = (x, y)
                                                
    return posx, posy, rot
        

def caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half):
    zz= 1
    if half == None:
        zz = 0.5
    x, y, n, tc, ty = fast_ray(x, y, zz, cos, sin, maph, n, i, ex, ey)
    h , c = shader(n, maph, mapc, sin, cos, x, y, i)
    if maph[int(x)][int(y)] == 0.5 and half == None:
        half = [h, c, n]
        x, y, n, tc2, ty2 = fast_ray(x, y, 1, cos, sin, maph, n, i, ex, ey)
        ty, tc = ty + ty2, tc + tc2
        h , c = shader(n, maph, mapc, sin, cos, x, y, i)
           
    return(c, h, x, y, n, half, ty, tc)


@njit(fastmath=True)
def fast_ray(x, y, z, cos, sin, maph, n, i, ex, ey):
    ty, tc = [], []
    while 1:
        n = n+1
        xx, yy = x, y
        x, y = x + cos, y + sin
        if z == 0.5 and (int(x*2) != int(xx*2) or int(y*2) != int(yy*2)):
            ty.append(-1/(0.02 * n*np.cos(np.deg2rad(i - 30))))
            if int(x) == ex and int(y) == ey:
                tc.append(np.asarray([0,0,1]))
            else:
                tc.append(np.asarray([0,0,0]))
        if maph[int(x)][int(y)] >= z:
            break        
    return x, y, n, tc, ty

def shader(n, maph, mapc, sin, cos, x, y, i):
    h = np.clip(1/(0.02 * n), 0, 1)#*np.cos(np.deg2rad(i-30))), 0, 1)
    c = np.asarray(mapc[int(x)][int(y)])*(0.4 + 0.6 * h)
    if maph[int(x+cos)][int(y-sin)] != 0:
        c = 0.85*c
        if maph[int(x-cos)][int(y+sin)] != 0 and sin >0:
            c = 0.7*c
    return h, c

def reflection(x, y, i, ex, ey, maph, mapc, sin, cos, n, c, h, half, pixels, ty, tc, height):
    hor = int(height/2)
    hh = int((h*height)/2)
    pixels[hor-hh:hor+hh,i] = np.add(pixels[hor-hh:hor+hh,i], np.asarray([c]*(hh*2)))/2
    if maph[int(x+cos)][int(y-sin)] != 0:
        cos = -cos
    else:
        sin = -sin
    c2, h2, x, y, n2, half2, ty2, tc2 = caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half)
    if n > n2:
        print(n, n2)
    ty, tc = ty + ty2, tc + tc2
    hh = int((h2*height)/2)
    pixels[hor-hh:hor+hh,i] = (c + c2)/2
    if half2 != None:
        hh = int((half2[0]*height)/2)
        pixels[hor:hor+hh,i] = (c + half2[1])/2
        
    if half != None:
        hh = int((half[0]*height)/2)
        pixels[hor:hor+hh,i] = half[1]
        
##    else:
##        plt.vlines(i, -h, h, lw = 8, colors = c, alpha=0.5) # draw vertical lines
##    if maph[int(x+cos)][int(y-sin)] != 0:
##        cos = -cos
##    else:
##        sin = -sin
##    c2, h, x, y, n, half2, tx, ty, tc = caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, tx, ty, tc)
##    c = (c + c2)/2
##    if half != None:
##        plt.vlines(i, 0, h, lw = 8, colors = c) # draw vertical lines
##    else:
##        plt.vlines(i, -h, h, lw = 8, colors = c) # draw vertical lines
##        if half2 !=  None:
##            plt.vlines(i, -half2[0], 0, lw = 8, colors = half2[1])        
    return pixels, ty, tc     

def draw_tiles(i, ty, tc, height, pixels):
##    for g in range(int(len(ty)/2)):
    for g in range(len(ty)-1):
        pf = np.clip((int((-ty[g]*height+height)/2)),0,height-1)
        pf2 = np.clip((int((-ty[g+1]*height+height)/2)),0,height-1)
        pixels[pf2:pf,i] = np.asarray([np.linspace(0,1,pf-pf2), np.linspace(0,1,pf-pf2), np.linspace(0,1,pf-pf2)]).T#(tc[g*2]+pixels[posf][i])/2
    return pixels

if __name__ == '__main__':
    main()
