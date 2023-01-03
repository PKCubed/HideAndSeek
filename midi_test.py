import pygame.midi
import time

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)
while True:
    player.note_on(64, 127)
    time.sleep(0.3)
    player.note_off(64, 127)
    time.sleep(0.05)
    player.note_on(65, 127)
    time.sleep(0.1)
    player.note_off(65, 127)
    time.sleep(0.2)
del player
pygame.midi.quit()