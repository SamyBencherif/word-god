#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
# @author: Samy Bencherif
# @copyright: May 2019

import pygame
import pygame.freetype
import sys
import random

r256 = lambda: random.randrange(256)

class Word:

    def __init__(self, text, pos):
        self.text = text
        self.origin = pos
        self.pos = pos
        self.color = (r256(), r256(), r256())


#words = [Word("love", (110,30)), Word("death", (110, 60))]
words = []
mapping = {}

ln = 1
try:
    gamefile = open("game.txt", "r")
except:
    sys.stderr.write("FATAL: game.txt not found!\n")
    sys.exit(1)

loc = 0

# Load Entry

entrydef = gamefile.readline()

if not entrydef:
    sys.stderr.write("FATAL: game.txt is empty!\n")
    sys.exit(1)

while entrydef and entrydef[0] in ("\n", "%"):
    entrydef = gamefile.readline()
    ln += 1

if not entrydef:
    sys.stderr.write("FATAL: Missing entry line.")
    sys.exit(1)

if entrydef.split("=")[0].strip() != "entry" or \
   len(entrydef.split("=")) != 2:
    sys.stderr.write("FATAL: (line %i) malformed entry line.\n" % ln)
    sys.exit(1)
else:
    for word in entrydef.split("=")[1].split(','):
        word = word.strip()
        words.append(Word(word, (20, 20 + loc*20)))
        loc += 1

ln += 1

# Load Rules

rule = 1
while rule:
    rule = gamefile.readline()
    while rule and rule[0] in ("\n", "%"):
        rule = gamefile.readline()
        ln += 1

    if rule:
        # A + B = C
        try:
            A = rule.split("+")[0].strip()
            B = rule.split("+")[1].split("=")[0].strip()
            C = rule.split("=")[1].strip().split("+")

            mapping.update( {tuple(sorted([A,B])):C} )
        except:
            sys.stderr.write("FATAL: (line %i)" % ln)
            sys.stderr.write(" malformed rule.\n")
            sys.exit(1)

    ln += 1

pygame.init()

disp = pygame.display.set_mode((640, 700))
font = pygame.freetype.SysFont('Consolas', 14)

mouseIsDown = False
target = None


for word in words:
    _, word.bounds = font.render(word.text)

while True:

    disp.fill((255,255,255))

    for word in words:
        Wsurf, _ = font.render(word.text, word.color)

        buffer = pygame.Surface((word.bounds.w, word.bounds.h))
        buffer.fill((255, 255, 255))
        buffer.blit(Wsurf, pygame.Rect(0, 0, word.bounds.w,
                                             word.bounds.h))
        buffer.set_alpha(120)

        disp.blit(buffer, word.origin)

        Wsurf, _ = font.render(word.text, word.color)
        disp.blit(Wsurf, word.pos)

        if target == None:
            for word2 in words:
                if word.pos[0] < word2.pos[0] + word2.bounds.w and \
                   word2.pos[0] < word.pos[0] + word.bounds.w and \
                   word.pos[1] < word2.pos[1] + word2.bounds.h and \
                   word2.pos[1] < word.pos[1] + word.bounds.h and \
                   word != word2:

                    # Two words are put together

                    newpos = ((word.pos[0] + word2.pos[0])/2,
                               (word.pos[1] + word2.pos[1])/2)


                    key = tuple(sorted([word.text, word2.text]))
                    if key in \
                       mapping.keys():
                        # there was a match

                        for newWord in mapping[key]:
                            newWord = newWord.strip()

                            # Do not create duplicates
                            if newWord in [x.text for x in words]:
                                continue

                            words.append(Word(newWord,
                                         word.pos))
                            _, words[-1].bounds = font.render(
                                    words[-1].text)

                            word.pos = word.origin
                            word2.pos = word2.origin

                            #loc += 1

    if target:
        try:
            target.pos = (event.pos[0] - target.bounds.w/2,
                          event.pos[1] - target.bounds.h/2)
        except:
            # player dragged word out of window
            target = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Exiting Successfully.")
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseIsDown = True
            mousePrevPos = event.pos

            for word in words:
               if word.pos[0] <= event.pos[0] and \
                  event.pos[0] <= word.pos[0] + word.bounds.w and \
                  word.pos[1] <= event.pos[1] and \
                  event.pos[1] <= word.pos[1] + word.bounds.h and \
                  target == None:
                   target = word
            if target == None:
                c = 0
                for word in words:
                    word.origin = (20+c//60, 20+20*c)
                    c += 1
                    word.pos = word.origin
        if event.type == pygame.MOUSEBUTTONUP:
            mouseIsDown = False
            target = None


    pygame.display.flip()
