# 
import pygame

mc = __import__('msgClient')

screen = pygame.display.set_mode((250, 100))


def control():
    displaysetup()
    #displaytext("Confidence")
    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

                ############################
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    displaytext("Left!")
                    mc.sendMsg("L")
                elif event.key == pygame.K_RIGHT:
                    displaytext("Right!")
                    mc.sendMsg("R")
                elif event.key == pygame.K_UP:
                    displaytext("Forward!")
                    mc.sendMsg("F")
                elif event.key == pygame.K_DOWN:
                    displaytext("Back!")
                    mc.sendMsg("B")
                elif event.key == pygame.K_SPACE:
                    displaytext("Stop!")
                    mc.sendMsg("S")
                elif event.key == pygame.K_KP4:
                    displaytext("Sweep LEft")
                    mc.sendMsg("Sweep_Left")
                elif event.key == pygame.K_KP6:
                    displaytext("Sweep Right!")
                    mc.sendMsg("Sweep_Right")
                elif event.key == pygame.K_KP8:
                    displaytext("Sweep Up!")
                    mc.sendMsg("Sweep_Up")
                elif event.key == pygame.K_KP2:
                    displaytext("Sweep Down!")
                    mc.sendMsg("Sweep_Down")
                elif event.key == pygame.K_ESCAPE:
                    print "Exit!"
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_w:
                    displaytext("Tilt Up!")
                    mc.sendMsg("Tilt_Up")
                elif event.key == pygame.K_x:
                    displaytext("Tilt Down!")
                    mc.sendMsg("Tilt_Down")
                elif event.key == pygame.K_a:
                    displaytext("Pan Left!")
                    mc.sendMsg("Pan_Left")
                elif event.key == pygame.K_d:
                    displaytext("Pan Right!")
                    mc.sendMsg("Pan_Right")
                elif event.key == pygame.K_s:
                    displaytext("Reset to Center!")
                    mc.sendMsg("Reset")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    print "Key released!"
                    if event.key == pygame.K_LEFT:
                        displaytext("Stop Left!")
                        mc.sendMsg("LS")
                    elif event.key == pygame.K_RIGHT:
                        displaytext("Stop Right!")
                        mc.sendMsg("RS")
                    elif event.key == pygame.K_UP:
                        displaytext("Stop Forward!")
                        mc.sendMsg("FS")
                    elif event.key == pygame.K_DOWN:
                        displaytext("Stop Back!")
                        mc.sendMsg("BS")
                    elif event.key == pygame.K_SPACE:
                        displaytext("Stop!")
                        mc.sendMsg("S")


                # print(str(ch))
                # pygame.exit()
                # exit()


##main()
def displaysetup():
    pygame.init()

    pygame.display.set_caption('Pi Control')
    pygame.key.set_repeat(500, 30)


def displaytext(msg):
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render(msg, 1, (10, 10, 10))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()



