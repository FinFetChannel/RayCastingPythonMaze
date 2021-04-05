import numpy as np
from matplotlib import pyplot as plt
import keyboard

size = 15 # random map generator
mapa = [[list(np.random.uniform(0, 1, 3))] * size for i in range(size)]
mapah = [[1] * size for i in range(size)]
for i in range(size-2):
    for j in range(size-2):
        mapah[i+1][j+1] = np.random.choice([0.3, 0.4, 0.7, 1])
        if np.random.uniform() > 0.33:
            mapa[i+1][j+1] = 0

posx, posy, posz = (1, np.random.randint(1, size -1), 0.5)
rot, rot_v = (np.pi/4, 0)
x, y, z = (posx, posy, posz)
mapa[x][y] = 0
count = 0 
while True:
    testx, testy = (x, y)
    if np.random.uniform() > 0.5:
        testx = testx + np.random.choice([-1, 1])
    else:
        testy = testy + np.random.choice([-1, 1])
    if testx > 0 and testx < size -1 and testy > 0 and testy < size -1:
        if mapa[testx][testy] == 0 or count > 5:
            count = 0
            x, y = (testx, testy)
            mapa[x][y] = 0
            if x == size-2:
                exitx, exity = (x, y)
                break
        else:
            count = count+1

mod = 1 # resolution modifier
inc = 0.05/mod # ray increment
height = int(48*mod)
width = int(60*mod)

while True: #main game loop
    pixels = []
    for j in range(height): #vertical loop 
        pixels.append([])
        rot_j = np.deg2rad(24 + rot_v - j/mod)
   
        for i in range(width): #horizontal vision loop
            rot_i = rot + np.deg2rad(i/mod - 30)
            x, y, z = (posx, posy, posz)
            sin, cos,  = (inc*np.sin(rot_i), inc*np.cos(rot_i))
            sinz = inc*np.sin(rot_j)
            n = 0
            while True: # ray loop
                x, y, z = (x + cos, y + sin, z + sinz)
                n = n+1
                if mapa[int(x)][int(y)] != 0 and z <= mapah[int(x)][int(y)]:
                    h = np.clip(1/(inc * n), 0, 1)
                    c = np.asarray(mapa[int(x)][int(y)])*(0.3 + 0.7 * h**2)
                    pixels[j].append(c)
                    break
                elif z > 1: # ceiling
                    h = 0.3 + 0.7*np.clip(1/(inc * n), 0, 1)**2
                    if int(x*5)%2 ==1:
                        pixels[j].append(np.asarray([.8,1,.9])*h)
                    else:
                        pixels[j].append(np.asarray([0.5,0.5,1])*h)
                    break
                elif z < 0: # floor
                    h = 0.3 + 0.7*np.clip(1/(inc * n), 0, 1)**2
                    if int(x) == exitx and int(y) == exity:
                        pixels[j].append(np.asarray([0,0,1]))
                    elif int(x*2)%2 == int(y*2)%2:
                        pixels[j].append(np.asarray([.3,.1,.1])*h)
                    else:
                        pixels[j].append(np.asarray([.8,.8,.5])*h)
                    break	 

    plt.imshow(pixels)
    plt.axis('off'); plt.tight_layout()
    plt.draw(); plt.pause(0.0001); plt.clf()

    # player's movement
    key = keyboard.read_key()
    x, y = (posx, posy)

    if key == 'up':
        x, y = (x + 0.3*np.cos(rot), y + 0.3*np.sin(rot))
    elif key == 'down':
        x, y = (x - 0.3*np.cos(rot), y - 0.3*np.sin(rot))
    elif key == 'left':
        rot = rot - np.pi/8
    elif key == 'right':
        rot = rot + np.pi/8
    elif key == '8':
        rot_v = rot_v + 10
    elif key == '2':
        rot_v = rot_v - 10
    elif key == 'esc':
        break

    if mapa[int(x)][int(y)] == 0:
        if int(posx) == exitx and int(posy) == exity:
            break
        posx, posy = (x, y)
        
plt.close()
    
