import pygame, random, math

pygame.init()
running = True
clock = pygame.time.Clock()

#speed multiplier, 1 is normal speed
speed_mult = 5

rocket_reached_target = False

#show display
pygame.display.set_caption('Smart Rockets')
width = 1000
height = 900
screen = pygame.display.set_mode((width,height))

#number of frames per generation
lifespan = 500

#Initialize rocket details
count = 0
gen = 1
maxFit = 0

#define target object which rockets aim for
class Target(object):
    def __init__(self):
        self.posx = int(width/2)
        self.posy = 50

    def display(self):
        pygame.draw.circle(screen, (255,0,255), (self.posx, self.posy), 10)

#Create rocket instructions AKA DNA
class DNA(object):
    def __init__(self):
        self.genes = []
        for i in range(lifespan):
            self.genes.append([random.uniform(-0.5,0.5), random.uniform(-0.5,0.5)])

#Defie rocket object
class Rocket(pygame.Surface):
    #position, velocity, and acceleration are x,y vectors
    def __init__(self, position, velocity, acceleration):
        self.v = velocity
        self.pos = position
        self.a = acceleration
        self.dna = DNA()
        self.stop = False
        self.hitTarget = False
        self.hitBar = False
        self.hitBottom = False
        self.r = random.randint(0,255)
        self.g = random.randint(0,255)
        self.b = random.randint(0,255)

    #Move rockets
    def applyForce(self, forcex, forcey):
        #reset acceleration to avoid acceleration growth
        self.a[0] *= 0
        self.a[1] *= 0
        #scale forces by arbitrary 0.6 and adjust acceleration
        self.a[0] += forcex*0.6
        self.a[1] += forcey*0.6

    #Update rocket postion, velocity, and acceleration
    def update(self):
        self.v[0] += self.a[0]
        self.v[1] += self.a[1]
        self.pos[0] += self.v[0]
        self.pos[1] -= self.v[1]
        self.applyForce(self.dna.genes[count][0],self.dna.genes[count][1])

    #Calculate fitness (based on distnace from target) in order to determine best rockets whose genes will be used in the next generation
    def calcFitness(self, targx, targy):
        d = math.hypot(self.pos[0] - targx, self.pos[1]-targy)
        #Penalize fitness for hitting bar or bottom of screen
        if self.hitBar or self.hitBottom:
            return 3/(5*d)
        else:
            return 1/d

    #Check if rocket has hit edges of screen, target, or bar
    def checkEdges(self):
        #Hit left/right edges of screen
        if self.pos[0] < 0 or self.pos[0] > width - 10:
            self.stop = True
        #Hit bottom
        elif self.pos[1] < 0:
            self.stop = True
            self.hitBottom = True
        #Hit top
        elif self.pos[1] > height - 10:
            self.stop = True
        #Hit bar
        elif (self.pos[0] < width/2+(width-260)/2 and self.pos[0]+10 > width/2-(width-260)/2) and (self.pos[1] < height-185 and self.pos[1]+10 > height-200):
            self.stop = True
            self.hitBar = True
        #Hit Target
        elif (self.pos[0]+5 < width/2+ 10 and self.pos[0]+5 > width/2-10) and (self.pos[1]+5 < 60 and self.pos[1]+5 >40):
            self.hitTarget = True
            global rocket_reached_target
            rocket_reached_target = True
            self.stop = True
    #show rocket on screen
    def display(self):
        pygame.draw.rect(screen, (self.r,self.g,self.b) ,(self.pos[0],self.pos[1], 10, 10))

#define list to store rockets
rockets = []

def createRockets():
    gene_pool = []
    #create 200 rockets with 0 velocity and 0 acceleration
    for rocket in range(200):
        rockets.append(Rocket([width/2 - 5, height-70],[0,0],[0,0]))
    if gen > 1:
        for rocket in prevRockets:
            #select top 20% of rockets and add to gene pool for next generation
            if rocket.calcFitness(width/2, 50)/maxFit > 0.80:
                gene_pool.append(rocket.dna)

        for rocket in rockets:
            #mutation
            if random.randint(0,10) == 5:
                rocket.dna = rocket.dna
            else:
                rand_index = random.randint(0,len(rocket.dna.genes)-100)
                newdna = random.choice(gene_pool)
                #randomly combine previous generation DNA with current DNA
                rocket.dna.genes = newdna.genes[:rand_index] + rocket.dna.genes[rand_index:]

#Create target and Rockets
t = Target()
createRockets()

while running:
    #Check for window closure
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Create black screen
    screen.fill((0,0,0))

    #Show and move rockets
    for rocket in rockets:
        rocket.display()
        rocket.checkEdges()
        if not rocket.stop:
            rocket.update()
    #show target
    t.display()
    #Create bar
    pygame.draw.rect(screen, (255,0,0),(width/2-(width-260)/2, height-200, width-260, 15))
    if count < lifespan-1:
        count += 1
    else:
        #find max fitness among current generation
        maxFit = 0
        for rocket in rockets:
            a = rocket.calcFitness(width/2, 50)
            if a > maxFit:
                maxFit = a

        #Create next generation of rockets
        count = 0
        gen += 1
        prevRockets = rockets
        rockets = []
        createRockets()
        prevRockets = []
    print('count: ' + str(count+1) + '  Generation: ' + str(gen))
    if rocket_reached_target == True:
        running = False
        print ('A rocket reached the target in ' + str(gen) + ' generations')

    #Next frame
    pygame.display.flip()
    clock.tick(60 * speed_mult)

pygame.quit()
