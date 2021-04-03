import numpy as np
from matplotlib import pyplot as plt
import keyboard

#random map generator
size = 15
mapa = [[list(np.random.uniform(0, 1, 3))] * size for i in range(size)]
for i in range(size-2):
    for j in range(size-2):
        if np.random.uniform() > 0.33:
            mapa[i+1][j+1] = 0

posx, posy = (1, np.random.randint(1, size -1))
rot = np.pi/4
x, y = (posx, posy)
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

while True: #main game loop
    
    plt.hlines(-0.6, 0, 60, colors='gray', lw=165, alpha=0.5)
    plt.hlines(0.6, 0, 60, colors='lightblue', lw=165, alpha=0.5)
    tilex, tiley, tilec = ([], [], [])
    
    for i in range(60): #vision loop
        rot_i = rot + np.deg2rad(i - 30)
        x, y = (posx, posy)
        sin, cos = (0.02*np.sin(rot_i), 0.02*np.cos(rot_i))
        n = 0
        while True: # ray loop
            xx, yy = (x, y)
            x, y = (x + cos, y + sin)
            n = n+1
            if abs(int(3*xx)-int(3*x)) > 0 or abs(int(3*yy)-int(3*y))>0:
                tilex.append(i)
##                tiley.append(-1/(0.02 * n))
                tiley.append(-1/(0.02 * n*np.cos(np.deg2rad(i - 30))))
                if int(x) == exitx and int(y) == exity:
                    tilec.append('b')
                else:
                    tilec.append('k')
                    
            if mapa[int(x)][int(y)] != 0:
##                h = np.clip(1/(0.02 * n), 0, 1)
                h = np.clip(1/(0.02 * n*np.cos(np.deg2rad(i-30))), 0, 1)
                c = np.asarray(mapa[int(x)][int(y)])*(0.3 + 0.7 * h**2)
                break 
        plt.vlines(i, -h, h, lw = 8, colors = c) # draw vertical lines

    plt.scatter(tilex, tiley, c=tilec) # draw tiles on the floor
    
    plt.axis('off'); plt.tight_layout(); plt.axis([0, 60, -1, 1])
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
    elif key == 'esc':
        break

    if mapa[int(x)][int(y)] == 0:
        if int(posx) == exitx and int(posy) == exity:
            break
        posx, posy = (x, y)

plt.close()

