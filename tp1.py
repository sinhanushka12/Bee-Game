from cmu_graphics import *
import random, time
import math

class player:
    
    def __init__(self):
        self.x = 350 
        self.y = 350
        self.velocityX = 0
        self.velocityY = 0
        self.constant = 0.5
        self.pollenInventory = []

    def drawPlayer(self, app):
        drawCircle(self.x, self.y, 50, fill='yellow')
        numFlowers = 0
        colors = []
        for flower in app.player.pollenInventory:
            if flower.color not in colors:
                drawCircle(self.x+ numFlowers*20, self.y + 50, 10, fill=flower.color)
                colors.append(flower.color)
                numFlowers += 1

    def playerOnStep(self):
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
        if abs(((self.x - flower.x)**2 + (self.y + flower.radius - flower.y)**2)**0.5 - flower.radius)< 30:
            return True
        return False
#-------------------------------------------------------------------


class Flower:
     
    def __init__(self, app):
        self.y = app.height + 40
        self.x = random.randrange(app.width)
        self.startX = self.x
        self.velocityY = -5
        self.c = 0.01
        self.radius = random.randrange(25, 35)
        # colors
        c = ['cornflowerBlue', 'violet', 'crimson']
        self.color = random.choice(c)
        # whether the flower is a pollinator or a flower that can be pollinated
        types = ['pollinator', 'notAPollinator']
        self.type = random.choice(types) 
        # attribute to indicate if it's been gathered
        self.gathered = False     
        self.id = time.time()
        # for gradual growth after pollination
        self.pollinated = 0

    def drawFlower(self):
        if self.type == 'pollinator': 
            # solid circle
            drawCircle(self.x, self.y, self.radius, 
                        fill = self.color)
        elif self.type == 'notAPollinator':
            # ringed circle
            if self.pollinated == 0:
                drawCircle(self.x, self.y, self.radius, fill= None,
                        border= self.color, borderWidth= 6) 
                drawCircle(self.x, self.y, self.radius-12, fill= self.color)  
            else:   
                drawCircle(self.x, self.y, self.radius, fill= None,
                        border= self.color, borderWidth= 6)   

    def flowerOnStep(self):
        self.x = self.startX + 200*math.sin(self.c*self.y)
        self.y += self.velocityY
    
    def flowerOffCanvas(self, app):
        if (self.y < 0):
            return True
        return False
#-------------------------------------------------------------------

def onAppStart(app):
    app.player = player()
    app.flowerList = []
    app.lastFlowerTime = time.time() 

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = "mediumAquamarine")
    app.player.drawPlayer(app)
    # gradual growth
    for flower in app.flowerList:
        if (flower.pollinated > 0) and (flower.pollinated < 1):
            flower.pollinated += 0.2
            flower.radius *= 1.05
        flower.drawFlower()
    point = 40
    for flower in app.player.pollenInventory:
        drawCircle(point , 40 , 15 + 20*flower.pollinated , fill = None, border = flower.color, borderWidth = 8)
        point += 25
        if flower.pollinated > 1:
            app.player.pollenInventory.remove(flower)

def onMouseMove(app, mouseX, mouseY):
    app.player.playerOnMouse(mouseX, mouseY)
    pollination(app)

def onStep(app):
    # step for the player
    app.player.removePollen()
    app.player.playerOnStep()
    
    
    # move one step and remove flowers if beyong the canvas
    for flower in app.flowerList:
        flower.flowerOnStep()
        if flower.flowerOffCanvas(app):
            app.flowerList.remove(flower)

    # add flowers
    if (time.time() - app.lastFlowerTime > 0.5):
        app.flowerList.append(Flower(app))
        app.lastFlowerTime = time.time()
       
    

def pollination(app):
    for flower in app.flowerList:
        # if the player is near a flower
        if app.player.nearAFlower(flower):
            if (flower.type == 'pollinator') and (flower.gathered == False):
                flower.gathered = True
                app.player.pollenInventory.append(flower)
            elif (flower.type == 'notAPollinator'):
                for donor in app.player.pollenInventory:
                    if (donor.color == flower.color)and(flower.pollinated == 0)and(donor.pollinated == 0):
                        #donor and acceptor can grow just once
                        # should be gradual growth 
                            flower.pollinated = 0.1
                            donor.pollinated = 0.1
                            
                        
            #add pollen underneath bee's feet


def main():
    runApp(width = 700, height = 700)

main()