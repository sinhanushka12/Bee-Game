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

    def nearAFlower(self,flower):
        if flower == None:
            return False
        elif flower.flowerOffCanvas():
            return False
        elif abs(((self.x - flower.x)**2 + (self.y + flower.radius - flower.y)**2)**0.5 - flower.radius)< 30:
            return True
        return False


    def pollination(self,app):
        for flower in app.flowerList:
            # if the player is near a flower
            if self.nearAFlower(flower):
                # ringed circle
                if (flower.type == 'pollinator') and (flower.gathered == False):
                    flower.gathered = True
                    self.pollenInventory.append(flower)
                elif (flower.type == 'notAPollinator'):
                    for donor in self.pollenInventory:
                        if (donor.color == flower.color)and(flower.pollinated == 0)and(donor.pollinated == 0):
                            #donor and acceptor can grow just once
                            # should be gradual growth 
                                flower.pollinated = 0.1
                                donor.pollinated = 0.1
                                flower.pollenPair = donor
                                donor.pollenPair = flower

# ------------------------------------------------------------------------------------------------------

class selfPlayer(player):
    
    def __init__(self, typeOfBee):
        super().__init__(typeOfBee)
        self.x = random.randint(200, 500)
        self.y = random.randint(200, 500)
        self.target = None 
        self.other = None
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
        self.Constant = 0.1

        #Set sprite counters
        #self.stepCounter = 0
        self.spriteCounter = 0

    def helperOnStep(self, app):
        if (self.target != None) and (self.nearAFlower(self.target)):
            self.nearTheTarget(app)
        elif (self.target != None):
            self.moveToTheTarget(app)
        else:
            self.updateTarget(app)
            self.moveToTheTarget(app)
       
        self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/10 + abs(self.velocityY)/10))
                                 % len(self.leftSpriteList))
        #self.stepCounter = 0
        if (self.y >= 700):
            self.y = 700
            self.velocityY = 0
        if (self.y <= 20):
            self.y = 30
            self.velocityY = 0
        if (self.x >= 700):
            self.x = 700
            self.velocityX = 0
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 0
    """
    These bees always choose a target based on the closest flower that is either 
        A) an ungathered pollinator with a color that the bee is not currently carrying or 
        B) an unpollinated flower that the bee is carrying the correct color for

    """
    def moveToTheTarget(self, app):
        if (self.target != None):
            if not (self.target.flowerOffCanvas()):
                self.velocityX = (self.target.x - self.x)*self.Constant
                self.velocityY = (self.target.y - self.y)*self.Constant
                self.x += self.velocityX
                self.y += self.velocityY
            else:
                self.velocityX = 0
                self.velocityY = 0
                self.updateTarget(app)               
        else:
            self.velocityX = 0
            self.velocityY = 0

    def updateTarget(self, app):
        colorSet = set()
        for pollen in self.pollenInventory:
            if pollen.color not in colorSet:
                colorSet.add(pollen.color)
        distFromFlower = dict()
        for f in app.flowerList:
            if (f.color not in colorSet) and (f.type == "pollinator") and (f.gathered == False) and (f.y< 600) and (self.other.target != f):
                distFromFlower[f] = distance(self.x, self.y, f.x, f.y)
            elif (f.color in colorSet) and (f.type == "notAPollinator") and (f.pollinated == 0)and (f.y< 600) and (self.other.target != f):
                distFromFlower[f] = distance(self.x, self.y, f.x, f.y)
        if distFromFlower:
            nearestFlower = min(distFromFlower, key= distFromFlower.get)
            self.target = nearestFlower
        else:
            self.target = None

    def nearTheTarget(self, app):
        # make sure to complete the pollination process
        if (self.target.type == "notAPollinator") :
            if self.target.pollinated < 5:
                self.x = self.target.x
                self.y = self.target.y - 35
            else:
                self.updateTarget(app)
        elif (self.target.type == "pollinator"): 
            # self.target.gathered = True
            # # once captured pollen, add to the inventory, not a target anymore
            # self.pollenInventory.append(self.target)
            self.updateTarget(app)
        else:
            self.target = None

    def drawHelper(self, app):
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
        for flower in self.pollenInventory:
            if flower.color not in colors:
                drawCircle(self.x+ numFlowers*13, self.y + 33, 10, fill=flower.color)
                colors.append(flower.color)
                numFlowers += 1

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
    
    def flowerOffCanvas(self):
        if (self.y < 0):
            return True
        return False
# -----------------------------------------------------------------------------------------------------------------------------------------------

def onAppStart(app):
    app.player = player('playerBee')
    app.helperBee1 = selfPlayer('helperBee')
    app.helperBee2 = selfPlayer('helperBee')
    app.helperBee1.other = app.helperBee2
    app.helperBee2.other = app.helperBee1
    app.flowerList = []
    app.lastFlowerTime = time.time() 
    # app.image = Image.open('background.png')
    # app.image = CMUImage(app.image)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = "aquamarine")
    #drawImage(app.image, 50, 100, width=200, height=200)
    app.player.drawPlayer(app)
    app.helperBee1.drawHelper(app)
    app.helperBee2.drawHelper(app)
    # gradual growth

    # if the ring is still on canvas, and the bee goes near a ringed circle,:
        # both of them should grow

    for flower in app.flowerList:
        if (flower.pollinated > 0) and (flower.pollinated < 5):
            if((flower.type == "notAPollinator") and 
                ((app.player.nearAFlower(flower)) or (app.helperBee1.nearAFlower(app.helperBee1.target)) or 
                    (app.helperBee2.nearAFlower(app.helperBee2.target)))):
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
    app.player.pollination(app)

def onStep(app):
    # step for the player
    app.player.removePollen()
    app.player.playerOnStep()
    app.helperBee1.helperOnStep(app)
    app.helperBee2.helperOnStep(app)
    app.helperBee1.pollination(app)
    app.helperBee2.pollination(app)
    
    # move one step and remove flowers if beyong the canvas
    for flower in app.flowerList:
        flower.flowerOnStep()
        if flower.flowerOffCanvas():
            app.flowerList.remove(flower)

    # add flowers
    if (time.time() - app.lastFlowerTime > 1):
        app.flowerList.append(Flower(app))
        app.lastFlowerTime = time.time()
       

def main():
    runApp(width = 700, height = 700)

main()
