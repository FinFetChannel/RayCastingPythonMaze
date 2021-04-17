# RayCastingPythonMaze

 ![](gif.gif)
 
A very simple 3D maze game made from scratch in python, using only three libraries:
- Numpy
- Matplotlib
- Keyboard

Based on the Ray Casting technique, where the objects are drawn entirely out of vertical lines. The size and position of the lines is defined by the distance between the player and the object.

Video tutorial here: https://youtu.be/5xyeWBxmqzc

## Basic setup

We will begin with a very simple map, later we will make a random map generator. The map is defined by a simple matrix, where ones represent walls and zeros represent corridors or empty spaces.

```python
import numpy as np
from matplotlib import pyplot as plt
import keyboard

mapa = [[1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1]]
```
We also need to set a starting position and direction for the player, and the exit coordinates:

```python
posx, posy, rot = 1.5, 1.5, np.pi/4
exitx, exity = 3, 3
```
Now we can star the vision loop, with a horizontal field of view of 60°, advancing one degree per iteration. The first ray will start 30° to the right of the player and the last one will be at 30° to the left. The ray always starts at the player's position, with increments based on sine and cosine of the ray angle on a infinite loop. A counter is used to keep the distance value the ray has traveled, otherwise one could simply use Pythagoras theorem to calculate the distance at the end.

To test if a ray has hit a wall we just have to check the integer parts of the ray coordinates against the map. If there was a hit we calculate a height and break out of the while loop. after that we draw a vertical line on position i going from -h to h.

```python
for i in range(60):
    rot_i = rot + np.deg2rad(i-30)
    x, y = posx, posy
    sin, cos = 0.02*np.sin(rot_i), 0.02*np.cos(rot_i)
    n = 0
    
    while 1:
        x, y, n = x + cos, y + sin, n +1
        if mapa[int(x)][int(y)]:
            h = 1/(0.02*n)
            break
        
    plt.vlines(i, -h, h)    
```

Proto ray tracing: https://youtu.be/ravnXknUvvQ

Ray casting 2.0 video: https://youtu.be/WhmTa1NGLSE

 
 
<img src="https://avatars0.githubusercontent.com/u/76776190?s=460&u=8f3943b46a0f1060a462d8a2922319edd9cd241c&v=4" width="100" height="100">
