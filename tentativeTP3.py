# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from cmu_graphics import *
from PIL import Image
import random, time
import math

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CLASS PLAYER

class player:

    def __init__(self, app, typeOfBee):
        self.typeOfBee = typeOfBee
        
        myGif = Image.open('images/giphy.gif')
        # Bee Gif from: https://www.pinterest.com/pin/cute-animated-honey-bee-gifs-at-best-animations-clipart-best-clipart-best--673077106817108502/

        self.leftSpriteList = []
        self.rightSpriteList = []

        for frame in range(myGif.n_frames): 
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.convert("RGBA")
            fr = CMUImage(fr)
            self.rightSpriteList.append(fr)
            
        for frame in range(myGif.n_frames):
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.convert("RGBA")
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.leftSpriteList.append(fr)

        self.leftSpriteList.pop(0)
        self.rightSpriteList.pop(0)

        self.spriteCounter = 0
        self.radius = 50
        self.accelerationX = 0
        self.accelerationY = 0
        self.x = app.width/2 
        self.y = app.height/2
        self.velocityX = 0
        self.velocityY = 0
        self.constant = 0.005 
        self.pollenInventory = []
        self.threshold = 5

    def drawPlayer(self, app):
        if self.velocityX < 0:
            drawImage(self.leftSpriteList[math.floor(self.spriteCounter)], 
            self.x, self.y, align = 'center')
        else:
            drawImage(self.rightSpriteList[math.floor(self.spriteCounter)], 
            self.x, self.y, align = 'center')

        # draw flower under the bee's feet
        numFlowers = 0
        colors = []
        for flower in app.player.pollenInventory:
            if flower.color not in colors:
                drawCircle(self.x+ numFlowers*20, self.y + 50, 10, fill=flower.color)
                colors.append(flower.color)
                numFlowers += 1

    def playerOnStep(self, app):
        # higher self.constant makes acceleration higher which makes it more difficult to control the bee
        self.constant = 0.005*app.difficulty 
        if abs(self.velocityX)+abs(self.velocityY) < self.threshold:
            self.spriteCounter = (self.spriteCounter + 0.1)% len(self.leftSpriteList)
        else:
            self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/100 
                                    + abs(self.velocityY)/100))% len(self.leftSpriteList))
        
        self.x += self.velocityX
        self.y += self.velocityY
        
        if (self.y >= app.height):
            self.y = app.height
            self.velocityY = 0
        if (self.y <= 0):
            self.y = 0
            self.velocityY =0
        if (self.x >= app.width):
            self.x = app.width
            self.velocityX = 0
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 0


    def playerOnMouse(self, newX, newY):
        self.accelerationX = (newX - self.x)*self.constant/(len(self.pollenInventory)+1)
        self.accelerationY = (newY - self.y)*self.constant/(len(self.pollenInventory)+1)
        self.velocityX += self.accelerationX
        self.velocityY += self.accelerationY

    def removePollen(self):
        # when pollen count > 6, remove the oldest pollen
        if len(self.pollenInventory) > 6:
            self.pollenInventory.pop(0)

    def nearAFlower(self,flower):
        if flower == None:
            return False
        elif flower.flowerOffCanvas():
            return False
        elif (((self.x - flower.x)**2 + 
                (self.y+self.radius - flower.y)**2)**0.5 < 2*flower.radius):
            return True
        return False


    def pollination(self,app):
        for flower in app.flowerList:
            if self.nearAFlower(flower):
                if (flower.type == 'pollinator') and (flower.gathered == False):
                    flower.gathered = True
                    self.pollenInventory.append(flower)
                elif (flower.type == 'notAPollinator'):
                    for donor in self.pollenInventory:
                        if (donor.color == flower.color)and(flower.pollinated == 0)and(donor.pollinated == 0):
                                flower.pollinated = 0.1
                                donor.pollinated = 0.1
                                flower.pollenPair = donor
                                donor.pollenPair = flower

    def collision(self, app):
        # making collision much liklier if difficulty is high.
        for r in app.rockList:
            if (distance(self.x, self.y, r.x, r.y) < 
                    (self.radius + (app.difficulty-1)*max(r.width, r.height)/2)): 
                self.velocityX = 0
                self.velocityY = 0
             

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CLASS SELF PLAYER: Helper Bee

class selfPlayer(player):
    
    def __init__(self, app, typeOfBee):
        super().__init__(app, typeOfBee)

        self.x = random.randint(200, app.width - 200)
        self.y = random.randint(200, app.height-200)
        self.target = None 
        self.other = None

        myGif = Image.open('images/giphy.gif') 
        self.leftSpriteList = []
        self.rightSpriteList = []

        for frame in range(myGif.n_frames):  
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//3, myGif.size[1]//3)) 
            fr = fr.convert("RGBA")
            fr = CMUImage(fr)
            self.rightSpriteList.append(fr)
            self.radius = 33
        
        for frame in range(myGif.n_frames):
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//3, myGif.size[1]//3))  
            fr = fr.convert("RGBA")
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.leftSpriteList.append(fr)

        self.leftSpriteList.pop(0)
        self.rightSpriteList.pop(0)
        self.Constant = 0.15
        self.spriteCounter = 0

    def helperOnStep(self, app):
        # lower self.constant for helper bees makes them slower in helping the player
        self.Constant = 0.15/(1+0.5*(app.difficulty-1)) 
        if (self.target != None):
            if (self.nearAFlower(self.target)):
                self.nearTheTarget(app)
            else:
                self.moveToTheTarget(app)
        else:
            self.updateTarget(app)
            if self.target != None:
                self.moveToTheTarget(app)
        
        if abs(self.velocityX)+abs(self.velocityY) < self.threshold:
            self.spriteCounter = (self.spriteCounter + 0.1)% len(self.leftSpriteList)
        else:
            self.spriteCounter = ((self.spriteCounter + 1 + math.floor(abs(self.velocityX)/100 
                                    + abs(self.velocityY)/100))% len(self.leftSpriteList))
        
        if (self.y >= app.height):
            self.y = app.height
            self.velocityY = 0
        if (self.y <= 20):
            self.y = 30
            self.velocityY = 0
        if (self.x >= app.width):
            self.x = app.width
            self.velocityX = 0
        if (self.x <= 0):
            self.x = 0
            self.velocityX = 0

    def moveToTheTarget(self, app):
        if (self.target != None):
            if not (self.target.flowerOffCanvas()):
                self.velocityX = (self.target.x- self.x)*self.Constant
                self.velocityY = (self.target.y - self.y)*self.Constant
                self.x += self.velocityX 
                self.y += self.velocityY 
            elif ((self.target.type == "notAPollinator") and 
                    (not (self.target.color in self.pollenInventory))):
                self.updateTarget(app)
            else:
                self.updateTarget(app)       

    def updateTarget(self, app):
        colorSet = set()
        for pollen in self.pollenInventory:
            if pollen.color not in colorSet:
                colorSet.add(pollen.color)
        distFromFlower = dict()
        for f in app.flowerList:
            if ((f.color not in colorSet) and (f.type == "pollinator") 
                and (f.gathered == False) and (f.y< app.height - 100) and (self.other.target != f)):
                distFromFlower[f] = distance(self.x, self.y, f.x, f.y)
            elif ((f.color in colorSet) and (f.type == "notAPollinator") and 
                (f.pollinated == 0)and (f.y< app.height -100) and (self.other.target != f)):
                distFromFlower[f] = distance(self.x, self.y, f.x, f.y)
        if distFromFlower:
            nearestFlower = min(distFromFlower, key= distFromFlower.get)
            self.target = nearestFlower
        else:
            self.target = None

    def nearTheTarget(self, app):
        if self.target.flowerOffCanvas():
            self.updateTarget(app)
        elif (self.target.type == "notAPollinator") :
            if (self.target.pollinated == 0):
                self.pollination(app)
                # helper bees contribute less to the score for same amount of work
                app.score += math.floor(100/self.target.radius) 
            elif self.target.pollinated < 5:
                self.moveToTheTarget(app)
            else:
                self.updateTarget(app)
        elif (self.target.type == "pollinator"): 
            self.target.gathered = True
            self.pollenInventory.append(self.target)
            self.updateTarget(app)

    def drawHelper(self, app):
        if self.velocityX < 0:
            drawImage(self.leftSpriteList[math.floor(self.spriteCounter)], 
            self.x, self.y, align = 'center')
        else:
            drawImage(self.rightSpriteList[math.floor(self.spriteCounter)], 
            self.x, self.y, align = 'center')

        numFlowers = 0
        colors = []
        for flower in self.pollenInventory:
            if flower.color not in colors:
                drawCircle(self.x+ numFlowers*13, self.y + 33, 10, fill=flower.color)
                colors.append(flower.color)
                numFlowers += 1

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CLASS FLOWER

class Flower:
     
    def __init__(self, app):
        self.y = app.height + 40
        self.x = random.randrange(app.width)
        self.startX = self.x
        self.c = 0.01
        self.amplitude = 200
        self.velocityX = self.amplitude*math.sin(self.c*self.y)
        self.velocityY = -2
        self.radius = random.randrange(25, 35)
        c = ['cornflowerBlue', 'violet', 'crimson']
        self.color = random.choice(c)
        types = ['pollinator', 'notAPollinator']
        self.type = random.choice(types) 
        self.gathered = False     
        self.id = time.time()
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

    def flowerOnStep(self, app):
        # higher frequency makes it harder to pollinate
        self.c = 0.01*app.difficulty 
        # if the flower has a high amplitude, it's difficult for bees to pollinate
        self.amplitude = 200*(app.difficulty/3 + 2/3) 
        self.x = self.startX +  self.amplitude*math.sin(self.c*self.y)
        self.y += self.velocityY
    
    def flowerOffCanvas(self):
        if (self.y < 0):
            return True
        return False
# -----------------------------------------------------------------------------------------------------------------------------------------------
# CLASS ROCK (obstacle)
class Rock:
     
    def __init__(self, app):
        self.y = app.height + 40
        self.x = random.randrange(app.width)
        self.width = random.randint(25,35)
        self.height = random.randint(25,35)
        self.startX = self.x
        self.c = 0.01
        self.amplitude = 200/(1/3+app.difficulty/3)
        self.velocityX = self.amplitude*math.sin(self.c*self.y)
        self.velocityY = -2
        self.radius = random.randrange(25, 35)
        self.color = "gray"
        
    def drawRock(self):   
        drawRect(self.x, self.y, self.width, self.height, fill = self.color)
            
    def rockOnStep(self, app):
        # higher frequency makes it harder to pollinate
        self.c = 0.01*app.difficulty 
        self.x = self.startX +  self.amplitude*math.sin(self.c*self.y)
        self.y += self.velocityY
    
    def rockOffCanvas(self):
        if (self.y < 0):
            return True
        return False

# -----------------------------------------------------------------------------------------------------------------------------------------------
# ANIMATIONS

def onAppStart(app):
    app.player = player(app, 'playerBee')
    app.helperBee1 = selfPlayer(app, 'helperBee')
    app.helperBee2 = selfPlayer(app, 'helperBee')
    app.helperBee1.other = app.helperBee2
    app.helperBee2.other = app.helperBee1
    app.allHelperBees = [app.helperBee1, app.helperBee2]
    app.flowerList = []
    app.rockList = []
    app.difficulty = 0
    app.lastFlowerTime = time.time() 
    app.lastRockTime = time.time()
    app.image = Image.open('images/background2.png')
    # Background image from: https://www.artstation.com/artwork/Vywl18
    app.image = CMUImage(app.image)
    app.score = 0
   

def game_redrawAll(app):
    drawImage(app.image, 0, 0, width= app.width, height=app.height)
    drawLabel(f"Score: {app.score}", 100, 70, size = 20, bold = True, fill = 'white' )
    
    app.player.drawPlayer(app)
    
    for helperBee in app.allHelperBees:
        helperBee.drawHelper(app)
    
    helperBee1 = app.allHelperBees[0]
    
    if len(app.allHelperBees) ==2:
        helperBee2 = app.allHelperBees[1]
    else:
        helperBee2 = selfPlayer(app, 'helperBee')
    
    for flower in app.flowerList:
        if (flower.pollinated > 0) and (flower.pollinated < 5):
            if((flower.type == "notAPollinator") and 
                ((app.player.nearAFlower(flower)) or (helperBee1.nearAFlower(helperBee1.target)) or 
                    (helperBee2.nearAFlower(helperBee2.target)))):
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
        if (flower.pollinated > 0) and (flower.pollinated < 1):
            # smaller flowers are harder to pollinate hence contribute more to score
            app.score += math.floor(150/flower.radius) 
    
    for r in app.rockList:
        r.drawRock()


def game_onStep(app):
    app.player.removePollen()
    app.player.playerOnStep(app)
    
    for helperBee in app.allHelperBees:
        helperBee.helperOnStep(app)
        helperBee.pollination(app)
        helperBee.collision(app)
        

    for flower in app.flowerList:
        flower.flowerOnStep(app)
        if flower.flowerOffCanvas():
            app.flowerList.remove(flower)
    
    for r in app.rockList:
        r.rockOnStep(app)
        if r.rockOffCanvas():
            app.rockList.remove(r)

    if (time.time() - app.lastFlowerTime > 1):
        app.flowerList.append(Flower(app))
        app.lastFlowerTime = time.time()

    if (time.time() - app.lastRockTime > 5):
        app.rockList.append(Rock(app))
        app.lastRockTime = time.time()

    if len(app.allHelperBees) < 2:
        app.allHelperBees.append(selfPlayer(app, 'helperBee'))

    for i in range(2):
        app.allHelperBees[i].other = app.allHelperBees[1-i]
    
    if app.score >= 2000:
        setActiveScreen("endGame")

def game_onMouseMove(app, mouseX, mouseY):
    app.player.playerOnMouse(mouseX, mouseY)
    app.player.pollination(app)
    app.player.collision(app)

def game_onKeyPress(app, key):
    if key == 'r':
        setActiveScreen("welcome")
    
# -----------------------------------------------------------------------------------------------------------------------------------------------
# Welcome Screen

def welcome_redrawAll(app):
    drawImage(app.image, 0, 0, width= app.width, height=app.height)
    drawLabel("Welcome to the Bee Game", app.width/2, app.height/2, size = 24, bold = True, fill = 'white')
    drawLabel("Press enter for more details", app.width/2, app.height/2 + 30, size = 20, bold = False, fill = 'white')

def welcome_onKeyPress(app, key):
    if key == "enter":
        setActiveScreen("moreDetails")

# -----------------------------------------------------------------------------------------------------------------------------------------------  
# More Details Screen

def moreDetails_redrawAll(app):
    drawImage(app.image, 0, 0, width= app.width, height=app.height)
    drawLabel("Move the player bee to the solid circles to get pollen", app.width/2, app.height/2, size = 24, bold = True, fill = 'white')
    drawLabel("Move the player bee to ringed circles to pollinate flowers", app.width/2, app.height/2 + 30, size = 20, bold = False, fill = 'white')
    drawLabel("Press E for easy", app.width/2, app.height/2 + 60, size = 18, bold = False, fill = 'white')
    drawLabel("Press M for medium", app.width/2, app.height/2 + 90, size = 18, bold = False, fill = 'white')
    drawLabel("Press D for difficult", app.width/2, app.height/2 + 120, size = 18, bold = False, fill = 'white')

def moreDetails_onKeyPress(app, key):
    if key == 'r': 
        setActiveScreen("welcome")
    if key == 'e':
        app.difficulty = 1
        setActiveScreen("game")
    if key == 'm':
        app.difficulty = 2
        setActiveScreen("game")
    if key == 'd':
        app.difficulty = 3
        setActiveScreen("game")
# -----------------------------------------------------------------------------------------------------------------------------------------------
# End Game Screen
def endGame_redrawAll(app):
    drawImage(app.image, 0, 0, width= app.width, height=app.height)
    drawLabel("You have won!", app.width/2, app.height/2, size = 24, bold = True, fill = 'white')

# -----------------------------------------------------------------------------------------------------------------------------------------------

def main():
    runAppWithScreens(initialScreen='welcome', width = 800, height = 500)

main()

# -----------------------------------------------------------------------------------------------------------------------------------------------
# CITATIONS

"""
Bee Gif: 
    https://giphy.com/explore/bee-sticker
    Found the bee gif on the above mentioned website. Unable to pinpoint where I went on the website or what 
    I searched for while looking for a bee gif. 
Canvas Background: 
    https://www.artstation.com/artwork/Vywl18
Code Inspiration: 
    For creating different screens, using OOP with animations, and working with GIFs: 
        15-112 Lectures by Professor Taylor
    S23 Scaffolded Project: Bee Game Google doc
    CS Academy assignments

"""
# -----------------------------------------------------------------------------------------------------------------------------------------------
