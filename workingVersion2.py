from cmu_graphics import *
from PIL import Image
import random, time
import math

# have two separate gifs: one that is left facing and one that is right facing
class player:

    def __init__(self, typeOfBee):
        self.typeOfBee = typeOfBee
        
        myGif = Image.open('images/giphy.gif') # right facing

        self.leftSpriteList = []
        self.rightSpriteList = []
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.convert("RGBA")
            fr = CMUImage(fr)
            self.rightSpriteList.append(fr)
            
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.convert("RGBA")
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.leftSpriteList.append(fr)

        ##Fix for broken transparency on frame 0
        self.leftSpriteList.pop(0)
        self.rightSpriteList.pop(0)

        #Set sprite counters
        #self.stepCounter = 0
        self.spriteCounter = 0

        
        self.x = 350 
        self.y = 350
        self.velocityX = 0
        self.velocityY = 0
        self.constant = 0.5
        self.pollenInventory = []

    def drawPlayer(self, app):
        #Draw current kirb sprite
        if self.velocityX < 0:
            drawImage(self.leftSpriteList[self.spriteCounter], 
            self.x, self.y, align = 'center')
        else:
            drawImage(self.rightSpriteList[self.spriteCounter], 
            self.x, self.y, align = 'center')

        numFlowers = 0
        # draw flower under the bee's feet
        colors = []
        for flower in app.player.pollenInventory:
            if flower.color not in colors:
                drawCircle(self.x+ numFlowers*20, self.y + 50, 10, fill=flower.color)
                colors.append(flower.color)
                numFlowers += 1

    def playerOnStep(self):
        #self.stepCounter += 1
        #if self.stepCounter >= 10: #Update the sprite every 10th call
        self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/10 + abs(self.velocityY)/10))
                                 % len(self.leftSpriteList))
        #self.stepCounter = 0
        
        self.x += self.velocityX
        self.y += self.velocityY
        
        if (self.y >= 700):
            self.y = 700
            self.velocityY = 0
        if (self.y <= 0):
            self.y = 0
            self.velocityY =0
        if (self.x >= 700):
            self.x = 700
            self.velocityX = 0
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 0


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

# ------------------------------------------------------------------------------------------------------

class selfPlayer(player):
    
    def __init__(self, typeOfBee):
        super().__init__(typeOfBee)
        self.x = random.randint(200, 500)
        self.y = random.randint(200, 500)
        self.target = None 

        myGif = Image.open('images/giphy.gif') # right facing

        self.leftSpriteList = []
        self.rightSpriteList = []
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//3, myGif.size[1]//3)) # smaller size helper bees
            fr = fr.convert("RGBA")
            fr = CMUImage(fr)
            self.rightSpriteList.append(fr)
            
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//3, myGif.size[1]//3))  # smaller size helper bees
            fr = fr.convert("RGBA")
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.leftSpriteList.append(fr)

        ##Fix for broken transparency on frame 0
        self.leftSpriteList.pop(0)
        self.rightSpriteList.pop(0)

        #Set sprite counters
        #self.stepCounter = 0
        self.spriteCounter = 0

    def helperOnStep(self, app):
        if (self.target != None) and (self.nearAFlower(self.target)):
            self.nearATarget(app)
        else:
            self.updateTarget(app)
        
        self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/10 + abs(self.velocityY)/10))
                                 % len(self.leftSpriteList))
        #self.stepCounter = 0
        
        self.x += self.velocityX
        self.y += self.velocityY
        
        if (self.y >= 700):
            self.y = 700
            self.velocityY = 0
        if (self.y <= 0):
            self.y = 0
            self.velocityY = 0
        if (self.x >= 700):
            self.x = 700
            self.velocityX = 0
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 0


    def updateTarget(self, app):
        # determine velocity when a target is acquired
        # target is not none
        if (self.target != None):
            if not (self.target.flowerOffCanvas(app)):
                self.target = None
            elif (self.target.type == "pollinator") and (self.target.gathered == False):
                self.velocityX = (self.target.x - self.x)*self.constant
                self.velocityY = (self.target.y - self.y)*self.constant
            elif (self.target.type == "notAPollinator") and (self.target.pollinated == 0):
                self.velocityX = (self.target.x - self.x)*self.constant
                self.velocityY = (self.target.y - self.y)*self.constant
            else:
                self.target = None
        else:
            self.target = self.nearestFlower(app)
            if self.target != None:
                self.velocityX = (self.target.x - self.x)*self.constant
                self.velocityY = (self.target.y - self.y)*self.constant


    def nearATarget(self, app):
        # make sure to complete the pollination process
        if (self.target.type == "notAPollinator") and (self.target.pollinated < 5):
            self.velocityX = self.target.velocityX
            self.velocityY = self.target.velocityY
        elif (self.target.type == "pollinator"): 
            self.target.gathered = True
            # once captured pollen, add to the inventory, not a target anymore
            self.pollenInventory.append(self.target)
            self.target = None
        else:
            self.target = None

    def nearestFlower(self, app):
        distances = dict()
        colorList = []
        for pollen in self.pollenInventory:
            colorList.append(pollen.color)
        for flower in app.flowerList:
            if (flower.type =="pollinator") and (flower.gathered == False):
                distances[flower] = distance(self.x, self.y, flower.x, flower.y)
            elif (flower.type == "notAPollinator") and (flower.pollinated == 0):
                if flower.color in colorList:
                    distances[flower] = distance(self.x, self.y, flower.x, flower.y)
        if not bool(distances):
            return None
        closestFlower = min(distances, key= distances.get)
        return closestFlower 
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Flower:
     
    def __init__(self, app):
        self.y = app.height + 40
        self.x = random.randrange(app.width)
        self.startX = self.x
        self.c = 0.01
        self.velocityX = 200*math.sin(self.c*self.y)
        self.velocityY = -2
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
        self.pollenPair = None

    def drawFlower(self):
        if self.type == 'pollinator': 
            # solid circle
            if self.gathered == False:
                drawCircle(self.x, self.y, self.radius, 
                        fill = self.color)
            else:
                # ring
                drawCircle(self.x, self.y, self.radius, fill= None,
                        border= self.color, borderWidth= 6) 
        elif self.type == 'notAPollinator':
            # ringed circle
            if (self.pollinated == 0) or (self.pollinated > 5):
                drawCircle(self.x, self.y, self.radius, fill= None,
                    border= self.color, borderWidth= 6) 
                drawCircle(self.x, self.y, self.radius-12, fill= self.color)   
            else:
                drawCircle(self.x, self.y, self.radius, fill= None,
                    border= self.color, borderWidth= 6) 
                drawCircle(self.x, self.y, self.radius-12, fill= None, 
                    border= self.color, borderWidth= 8)  

    def flowerOnStep(self):
        self.x = self.startX + 200*math.sin(self.c*self.y)
        self.y += self.velocityY
    
    def flowerOffCanvas(self, app):
        if (self.y < 0):
            return True
        return False
# -----------------------------------------------------------------------------------------------------------------------------------------------

def onAppStart(app):
    app.player = player('playerBee')
    app.helperBee1 = selfPlayer('helperBee')
    app.helperBee2 = selfPlayer('helperBee')
    app.flowerList = []
    app.lastFlowerTime = time.time() 

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = "aquamarine")
    app.player.drawPlayer(app)
    app.helperBee1.drawPlayer(app)
    app.helperBee2.drawPlayer(app)
    # gradual growth

    # if the ring is still on canvas, and the bee goes near a ringed circle,:
        # both of them should grow

    for flower in app.flowerList:
        if (flower.pollinated > 0) and (flower.pollinated < 5):
            if (flower.type == "notAPollinator") and app.player.nearAFlower(flower):
                flower.pollinated += 1
                flower.radius *= 1.05
                flower.pollenPair.pollinated += 1
                flower.pollenPair.radius *= 1.05 
        flower.drawFlower()
    point = 40
    for flower in app.player.pollenInventory:
        drawCircle(point , 40 , 15 + 7*flower.pollinated , fill = None, border = flower.color, borderWidth = 8)
        point += 25
        if flower.pollinated > 4:
            app.player.pollenInventory.remove(flower)

def onMouseMove(app, mouseX, mouseY):
    app.player.playerOnMouse(mouseX, mouseY)
    pollination(app)

def onStep(app):
    # step for the player
    app.player.removePollen()
    app.player.playerOnStep()
    app.helperBee1.helperOnStep(app)
    app.helperBee2.helperOnStep(app)
    
    
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
        if app.player.nearAFlower(flower):
            # ringed circle
            if (flower.type == 'pollinator') and (flower.gathered == False):
                flower.gathered = True
                app.player.pollenInventory.append(flower)
            elif (flower.type == 'notAPollinator'):
                for donor in app.player.pollenInventory[::-1]:
                    if (donor.color == flower.color)and(flower.pollinated == 0)and(donor.pollinated == 0):
                        #donor and acceptor can grow just once
                        # should be gradual growth 
                            flower.pollinated = 0.1
                            donor.pollinated = 0.1
                            flower.pollenPair = donor
                            donor.pollenPair = flower
                        



def main():
    runApp(width = 700, height = 700)

main()
