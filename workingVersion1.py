from cmu_graphics import *
from PIL import Image
import random, time
import math

class player:

    def __init__(self):
        myGif = Image.open('images/giphy.gif')
        self.spriteList = []
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.spriteList.append(fr)

        ##Fix for broken transparency on frame 0
        self.spriteList.pop(0)

        #Set sprite counters
        #self.stepCounter = 0
        self.spriteCounter = 0

        self.x = 350 
        self.y = 350
        self.velocityX = 0
        self.velocityY = 0
        self.constant = 0.5
        self.pollenInventory = []

    def drawPlayer(self):
        #Draw current kirb sprite
        drawImage(self.spriteList[self.spriteCounter], 
            self.x, self.y, align = 'center')
    
    def playerOnStep(self):
        #self.stepCounter += 1
        #if self.stepCounter >= 10: #Update the sprite every 10th call
        self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/10 + abs(self.velocityY)/10))
                                 % len(self.spriteList))
        #self.stepCounter = 0
        
        self.x += self.velocityX
        self.y += self.velocityY
        
        if (self.y >= 700):
            self.y = 700
            self.velocityY = -10
        if (self.y <= 0):
            self.y = 0
            self.velocityY = 10
        if (self.x >= 700):
            self.x = 700
            self.velocityX = -10
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 10


    def playerOnMouse(self, newX, newY):
        self.velocityX = (newX - self.x)*self.constant
        self.velocityY = (newY - self.y)*self.constant

    def removePollen(self):
        # when pollen count > 6, remove the oldest pollen
        if len(self.pollenInventory) > 6:
            self.pollenInventory.pop(0)

    def nearAFlower(self, flower):
        if ((self.x - flower.x)**2 + (self.y + self.radius -20 - flower.y)**2)**0.5 < flower.radius:
            return True
        return False

# ------------------------------------------------------------------------------------------------------

class Flower:
     
    def __init__(self, app):
        self.y = app.height + 40
        self.x = random.randrange(app.width)
        self.startX = self.x
        self.velocityY = -5
        self.c = 0.01
        self.radius = random.randrange(10, 25)
        # colors
        c = ['cornflowerBlue', 'violet', 'crimson']
        self.color = random.choice(c)
        # whether the flower is a pollinator or a flower that can be pollinated
        types = ['pollinator', 'notAPollinator']
        self.type = random.choice(types) 
        # attribute to indicate if it's been gathered
        self.gathered = False     
        self.id = time.time()

    def drawFlower(self):
        if self.type == 'pollinator': 
            # solid circle
            drawCircle(self.x, self.y, self.radius, 
                        fill = self.color)
        elif self.type == 'notAPollinator':
            # ringed circle
            drawCircle(self.x, self.y, self.radius, fill= None,
                        border= self.color, borderWidth= 4) 
            drawCircle(self.x, self.y, self.radius-6, fill= self.color)


    def flowerOnStep(self):
        self.x = self.startX + 200*math.sin(self.c*self.y)
        self.y += self.velocityY
    
    def flowerOffCanvas(self, app):
        if (self.y < 0):
            return True
        return False
    
# -----------------------------------------------------------------

def onAppStart(app):
    app.beePlayer = player()
    app.flowerList = []
    app.lastFlowerTime = time.time() 

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = "mediumAquamarine")
    app.beePlayer.drawPlayer()
    for flower in app.flowerList:
        flower.drawFlower()

def onMouseMove(app, mouseX, mouseY):
    app.beePlayer.playerOnMouse(mouseX, mouseY)

def onStep(app):
    # step for the player
    app.beePlayer.playerOnStep()

    
    # move one step and remove flowers if beyong the canvas
    for flower in app.flowerList:
        flower.flowerOnStep()
        if flower.flowerOffCanvas(app):
            app.flowerList.remove(flower)

    # add flowers
    if (time.time() - app.lastFlowerTime > 1):
        app.flowerList.append(Flower(app))
        app.lastFlowerTime = time.time()

def pollination(app):
    for flower in app.flowerList:
        # if the player is near a flower
        if app.beePlayer.nearAFlower(flower):
            if (flower.type == 'pollinator') and (flower.id not in app.beePlayer.pollenInventory):
                flower.gathered = True
                app.beePlayer.pollenInventory.append(flower.id)
            elif (flower.type == 'notAPollinator'):
                for donor in app.beePlayer.pollenInventory:
                    if donor.color == flower.color:
                        # should be gradual growth 
                        flower.radius += 30
                        donor.radius += 30
            #add pollen underneath bee's feet


def main():
    runApp(width = 700, height = 700)

main()