import numpy as np
from matplotlib import pyplot as plt
from pynput import keyboard, mouse
from time import time

def main():
    size = 15
    global key; key = None # register keypresses
    listener = keyboard.Listener(on_press=on_press);listener.start()
    last_mouse = [0,0]
    posx, posy, rot = (1, np.random.randint(1, size -1), 1) # player pos
    bg = np.linspace(0, 1, 150) #background gradient
    mapc, maph, mapr, ex, ey = maze_generator(posx, posy, size)# map, exit
    plt.figure(num = 'Pycaster 2.0')
    while True: #main game loop
        start = time()
        rot, last_mouse = rotation(rot, last_mouse)
        plt.hlines(-0.5, 0, 60, colors='k', lw=165, alpha=np.sin((rot+np.pi/2)/2)**2/2)
        plt.hlines(0.5, 0, 60, colors='k', lw=165, alpha=np.sin((rot-np.pi/2)/2)**2/2)
        plt.scatter([30]*150, -bg, c=-bg, s=200000, marker='_', cmap='Greys')
        plt.scatter([30]*150, bg, c=bg, s=200000, marker='_', cmap='Blues')
        tx, ty, tc = ([], [], [])
        for i in range(60): #vision loop
            rot_i = rot + np.deg2rad(i - 30)
            x, y = (posx, posy)
            sin, cos = (0.04*np.sin(rot_i), 0.04*np.cos(rot_i))
            n, half = 0, None
            c, h, x, y, n, half, tx, ty, tc = caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, tx, ty, tc)
            
            if mapr[int(x)][int(y)] == 1:
                c, h, x, y, n, half2, tx, ty, tc = reflection(x, y, i, ex, ey, maph, mapc, sin, cos, n, c, h, half, tx, ty, tc)

            else:
                plt.vlines(i, -h, h, lw = 8, colors = c)
                if half !=  None:
                    plt.vlines(i, -half[0], 0, lw = 8, colors = half[1])
            

            
        plt.axis('off'); plt.tight_layout(); plt.axis([0, 60, -1, 1])
        plt.scatter(tx, ty, c=tc, zorder = 2, alpha=0.5, marker='s') # draw ts on the floor
        plt.text(57, 0.9, str(round(1/(time()-start),1)), c='y')
        plt.draw();plt.pause(0.1); plt.clf()
        # player's movement
        posx, posy, rot, keyout = movement(posx, posy, rot, maph)
        if (int(posx) == ex and int(posy) == ey) or keyout == 'esc':
            break

    plt.close()

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

def rotation(rot, last_mouse): # for 1080p screen
    with mouse.Controller() as check:
        position = check.position
        if position[0] != last_mouse[0] or position[0]>1860 or position[0] < 60:
            delta = last_mouse[0] - position[0]
            if position[0]>1860:
                delta = 1860 - position[0]
            if position[0] < 60:
                delta = 60 - position[0]

            rot = rot + 4*np.pi*(0.5-delta/1920)


    return(rot, position)

def on_press(key_new):
    global key
    key = key_new
    
def movement(posx, posy, rot, maph):
    global key
    x, y = (posx, posy)
    keyout = None
    if key is not None:
        if key == keyboard.Key.up:
            x, y = (x + 0.3*np.cos(rot), y + 0.3*np.sin(rot))
        elif key == keyboard.Key.down:
            x, y = (x - 0.3*np.cos(rot), y - 0.3*np.sin(rot))
        elif key == keyboard.Key.left:
            rot = rot - np.pi/8
        elif key == keyboard.Key.right:
            rot = rot + np.pi/8
        elif key == keyboard.Key.esc:
            keyout = 'esc'
    key = None        
    if maph[int(x)][int(y)] == 0:
        posx, posy = (x, y)
        
    return posx, posy, rot, keyout

def caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, tx, ty, tc):
    while True: # ray loop
        xx, yy = (x, y)
        x, y = (x + cos, y + sin)
        n = n+1
        if half == None and int(x*2)%2 == int(y*2)%2:#(abs(int(3*xx)-int(3*x)) > 0 or abs(int(3*yy)-int(3*y))>0):
            tx.append(i)
            ty.append(-1/(0.04 * n*np.cos(np.deg2rad(i - 30))))
            if int(x) == ex and int(y) == ey:
                tc.append('b')
            else:
                tc.append('k')
        if maph[int(x)][int(y)] == 1 or (maph[int(x)][int(y)] == 0.5 and half == None):
            h , c = shader(n, maph, mapc, sin, cos, x, y, i)
            if maph[int(x)][int(y)] == 0.5 and half == None:
                half = [h, c, n]
            else:
                break

    return(c, h, x, y, n, half, tx, ty, tc)

def shader(n, maph, mapc, sin, cos, x, y, i):
    h = np.clip(1/(0.04 * n*np.cos(np.deg2rad(i-30))), 0, 1)
    c = np.asarray(mapc[int(x)][int(y)])*(0.4 + 0.6 * h)
    if maph[int(x+cos)][int(y-sin)] != 0:
        c = 0.85*c
        if maph[int(x-cos)][int(y+sin)] != 0 and sin >0:
            c = 0.7*c
    return h, c

def reflection(x, y, i, ex, ey, maph, mapc, sin, cos, n, c, h, half, tx, ty, tc):
    if half != None:
        plt.vlines(i, 0, h, lw = 8, colors = c, alpha=0.5) #top reflected
        plt.vlines(i, -half[0], 0, lw = 8, colors = half[1])# bottom regular
    else:
        plt.vlines(i, -h, h, lw = 8, colors = c, alpha=0.5) # draw vertical lines
    if maph[int(x+cos)][int(y-sin)] != 0:
        cos = -cos
    else:
        sin = -sin
    c2, h, x, y, n, half2, tx, ty, tc = caster(x, y, i, ex, ey, maph, mapc, sin, cos, n, half, tx, ty, tc)
    c = (c + c2)/2
    if half != None:
        plt.vlines(i, 0, h, lw = 8, colors = c) # draw vertical lines
    else:
        plt.vlines(i, -h, h, lw = 8, colors = c) # draw vertical lines
        if half2 !=  None:
            plt.vlines(i, -half2[0], 0, lw = 8, colors = half2[1])        
    return c, h, x, y, n, half2, tx, ty, tc     

if __name__ == '__main__':
    main()
