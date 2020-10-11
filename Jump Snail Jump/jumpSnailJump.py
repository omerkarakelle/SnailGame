import pygame
import sqlite3

pygame.init()
pygame.display.set_caption("Jump Snail Jump!")

screenWidth = 1200
screenHeight = 800

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

    def connectionClose(self):
        self.conn.commit()
        self.conn.close()

    def getMoney(self):
        self.cursor.execute("SELECT * FROM money")
        self.totalMoney = self.cursor.fetchall()
        Database.connectionClose(self)
        return self.totalMoney[0][0]

    def updateMoney(self,oldmoney,newmoney): #updating money that player has
        self.cursor.execute("UPDATE money SET totalmoney = ? WHERE totalmoney = ?", (newmoney,oldmoney))
        Database.connectionClose(self)

class Level(Database):
    def __init__(self,level):
        Database.__init__(self)
        self.cursor.execute("SELECT * FROM game" + str(level))
        self.values = self.cursor.fetchall()
        self.rectX = [i[0] for i in self.values]
        self.rectY = [i[1] for i in self.values]
        self.rectWidth = [i[2] for i in self.values]
        self.rectHeight = [i[3] for i in self.values]
        self.hrzntl = [i[4] for i in self.values]
        self.coins = [i[5] for i in self.values]
        Database.connectionClose(self)

class Snail(Database):
    def __init__(self):
        Database.__init__(self)
        self.image = [pygame.image.load("png/snail"+ str(number) +".png").convert_alpha() for number in range(5)]
        self.imageLeft = [pygame.image.load("png/snail"+ str(number) +"left.png").convert_alpha() for number in range(5)]
    def getSnail(self):
        self.cursor.execute("SELECT * FROM snail")
        self.snails = self.cursor.fetchall()
        Database.connectionClose(self)
        return self.snails
    def snailUnlock(self,curs):
        self.cursor.execute("UPDATE snail SET locked = 0 WHERE snails = ?",(curs,))
        Database.connectionClose(self)

def update(way):
    global horizontalChange,horizontalAcceleration, money
    screen.blit(pygame.transform.scale(background, (screenWidth, screenHeight)), (0, 0))
    for i in range(len(level.values)):
        if level.hrzntl[i] ==1:
            horizontalChange += horizontalAcceleration
            level.rectX[i] += horizontalChange
            if horizontalChange >=2 or horizontalChange <= -2:
                horizontalAcceleration *= -1
        if level.rectY[i] > -30 and level.rectY[i] <= 900:
            pygame.draw.rect(screen, (0, 0, 0), (int(level.rectX[i]), int(level.rectY[i]), level.rectWidth[i], level.rectHeight[i]))
        if level.coins[i] ==1: #blitting coins into screen
            distance = ((x-level.rectX[i])**2 + (y - (level.rectY[i] - 50))**2)**(1/2)
            if distance > 50:
                screen.blit(imageCoin, (level.rectX[i], level.rectY[i] - 50))
            else:
                Database().updateMoney(money, money + 1)
                money = money + 1
                level.coins[i] = 0 #deleting the picture of coin

    #updating the image of snail by checking its direction
    if way == "right":
        screen.blit(image, (int(x), int(y)))
    elif way == "left":
        screen.blit(imageLeft, (int(x), int(y)))

def isTouched():
    global y
    for i in range(len(level.values)): #checking if snail touchs any rectangle when it is falling
        if dy >= 0 and x <= level.rectX[i]+level.rectWidth[i] and x+64 >= level.rectX[i] and y+64 <= level.rectY[i] + 10 and y+64 >= level.rectY[i]:
            y = level.rectY[i] - 60
            return True
    return False

def locked(i):
    if snails[i][2] ==0:
        return False
    return True

def isGameOver():
    if y > 800:
        return True
    return False

def gameOver():
    main()

def main():
    global screen, background, rectX, rectY, rectWidth, rectHeight, image, imageLeft,x,y,dx,dy,gravity,level, imageCoin
    x = 200
    y = 500
    dx = 5
    dy = 0
    gravity = 0.2

    global money
    money = Database().getMoney()

    screen = pygame.display.set_mode((screenWidth,screenHeight))
    icon = pygame.image.load("png/snail0.png")
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    background = pygame.image.load("png/background.jpg").convert()
    speed = 100
    way = "right"

    cursor = 0 #cursor for snails
    levelCursor = 0 #cursor for levels
    pointer = "snails" #cursor for updown movements, it can be valued levels, snails and credit


    images = Snail().image #image list of all snail skins in the game
    imageLefts = Snail().imageLeft #image list of all snail skins in the game, but looking at left direction
    imageLock = pygame.image.load("png/lock.png").convert_alpha() #an image of lock, showing if a snail skin is bought or not
    imageJump = pygame.image.load("png/jump.png").convert_alpha() #a png image, used as header
    imageSelect = pygame.image.load("png/select.png").convert_alpha()
    imageStart = pygame.image.load("png/start.png").convert_alpha()
    levelImages = [pygame.image.load("png/{}.png".format(i)).convert_alpha() for i in range(2)]
    imageSelectLevel = pygame.image.load("png/selectlevel.png").convert_alpha()
    imageMoney = pygame.image.load("png/money.png").convert_alpha()
    imageMoneyHave = pygame.image.load("png/moneybig.png").convert_alpha()
    imageCoin = pygame.image.load("png/coin.png").convert_alpha()

    font = pygame.font.Font(None, 60)
    font2 = pygame.font.Font(None, 36)

    global snails
    snails = Snail().getSnail() #a list of all snails' features

    snailAnnouncement = [font2.render(str(i[1]), True, (0, 0, 0)) for i in snails]
    snailRect = [snailAnnouncement[i].get_rect(center=(225+200*i, 345)) for i in range(5)]

    announcement = font.render(str(money), True, (0, 0, 0))
    ar = announcement.get_rect(center=(75, 310))

    running = False
    firstMenu = True
    while firstMenu: #while loop for firt menu, which is showing snails (if they are bought or not),levels and money
        clock.tick(25)

        screen.blit(pygame.transform.scale(background, (screenWidth, screenHeight)), (0, 0))
        screen.blit(imageJump, (325, 50))
        screen.blit(imageStart, (430, 650))
        screen.blit(imageMoneyHave, (50, 225))
        screen.blit(announcement, ar)


        for i in range(5): #there are five snail skins and this loop is putting them into screen
            if cursor != i:
                if not locked(i):
                    screen.blit(images[i], (175 + 200*i, 250))
                else:
                    screen.blit(imageLock, (175 + 200 * i, 250))
                    screen.blit(imageMoney, (175 + 200*i, 330))
                    screen.blit(snailAnnouncement[i], snailRect[i])
            elif cursor == i:
                if not locked(i):
                    screen.blit(images[i], (175 + 200 * i, 200)) #if cursor is on the snail, then snail is showed
                else:
                    screen.blit(imageLock, (175 + 200 * i, 200))
                    screen.blit(imageMoney, (175 + 200*i, 330))
                    screen.blit(snailAnnouncement[i], snailRect[i])


        for i in range(2): #there are 2 levels
            if levelCursor == i:
                screen.blit(levelImages[i], (425 +175*i, 425))
            else:
                screen.blit(levelImages[i], (425 + 175 * i, 475))

        if pointer == "snails":
            screen.blit(imageSelect, (500, 360))
            pygame.draw.rect(screen, (0, 0, 0), (150, 190, 925, 210), 1)
        if pointer == "levels":
            screen.blit(imageSelectLevel, (500, 575))
            pygame.draw.rect(screen, (0, 0, 0), (350, 390, 500, 180), 1)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if pointer == "snails" and cursor != 4:
                        cursor += 1

                    elif pointer == "levels" and levelCursor != 1:
                        levelCursor +=1
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if pointer == "snails" and cursor != 0:
                        cursor -= 1
                    elif pointer == "levels" and levelCursor !=0 :
                        levelCursor -=1
                if event.key == pygame.K_DOWN:
                    pointer = "levels"
                if event.key == pygame.K_UP:
                    pointer = "snails"
                if event.key == pygame.K_RETURN:
                    if pointer =="levels" and not locked(cursor):
                        firstMenu = False
                        running = True
                        break
                    elif pointer == "snails" and not locked(cursor):
                        pointer = "levels"
                    elif money >= snails[cursor][1] and locked(cursor):
                        Snail().snailUnlock(cursor)
                        snails = Snail().getSnail()
                        Database().updateMoney(money,money-snails[cursor][1])
                        money = Database().getMoney()
        pygame.display.flip()


    level = Level(levelCursor)
    image = images[cursor]
    imageLeft = imageLefts[cursor]

    acceleration = 0.0005 #acceleration for rectangles falling
    change = 1 #first speed of rectangles falling
    global horizontalChange, horizontalAcceleration
    horizontalChange = 2
    horizontalAcceleration = -0.002

    while running: #while loop for gameplay
        clock.tick(speed)

        pressedKey = pygame.key.get_pressed()

        if pressedKey[pygame.K_d] or pressedKey[pygame.K_RIGHT]:
            x +=dx
            way = "right"
        if pressedKey[pygame.K_a] or pressedKey[pygame.K_LEFT] :
            x -=dx
            way = "left"

        if isTouched():
            dy = 0
            if pressedKey[pygame.K_SPACE] or pressedKey[pygame.K_w]:
                gravity = 0.2
                dy = -10
        else:
            dy += gravity
            y += dy
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        change += acceleration
        for i in range(len(level.values)):
            level.rectY[i] += change


        if isGameOver():
            gameOver()
            break


        update(way)
        pygame.display.flip()


if __name__ == "__main__":
    main()