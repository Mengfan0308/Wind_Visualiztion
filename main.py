import pygame
import pymunk
import pymunk.pygame_util

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
space = pymunk.Space()
draw_options = pymunk.pygame_util.DrawOptions(screen)

def create_tetris_piece(position):
    body = pymunk.Body(1, pymunk.moment_for_box(1, (40, 40)))
    body.position = position
    shape = pymunk.Poly.create_box(body, (40, 40))
    space.add(body, shape)
    return body

cannon_pos = (100, 300)
piece = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and piece is None:
            piece = create_tetris_piece(cannon_pos)
            piece.velocity = (400, 0)
        if event.type == pygame.KEYDOWN and piece:
            if event.key == pygame.K_LEFT:
                piece.angle += 0.1
            if event.key == pygame.K_RIGHT:
                piece.angle -= 0.1

    screen.fill((30, 30, 30))
    space.step(1/60)
    space.debug_draw(draw_options)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()