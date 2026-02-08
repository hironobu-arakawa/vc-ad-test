import sys
import numpy as np
import pygame

# --- VC-AD GENERATED CODE: DO NOT READ, JUST RUN ---
# Constitution: Speed > Readability
# Boundary: No Classes, Single Scope, Float32Array Only

COUNT = 50_000

pygame.init()
W, H = 960, 540
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("VC-AD Particle Demo (Python)")
clock = pygame.time.Clock()

# SoA layout with float32 arrays
P_X = np.random.rand(COUNT).astype(np.float32) * W
P_Y = np.random.rand(COUNT).astype(np.float32) * H
V_X = (np.random.rand(COUNT).astype(np.float32) - 0.5) * 4.2
V_Y = (np.random.rand(COUNT).astype(np.float32) - 0.5) * 4.2

# Colors as uint8 RGB triples
COLOR = (np.random.rand(COUNT, 3) * 255).astype(np.uint8)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update positions
    P_X += V_X
    P_Y += V_Y

    # Boundary bounce (vectorized)
    mask_x_low = P_X < 0
    mask_x_high = P_X > (W - 1)
    V_X[mask_x_low | mask_x_high] *= -1
    P_X = np.clip(P_X, 0, W - 1)

    mask_y_low = P_Y < 0
    mask_y_high = P_Y > (H - 1)
    V_Y[mask_y_low | mask_y_high] *= -1
    P_Y = np.clip(P_Y, 0, H - 1)

    # Draw via direct buffer access
    arr = pygame.surfarray.pixels3d(screen)
    arr[:] = 0

    xi = P_X.astype(np.int32)
    yi = P_Y.astype(np.int32)
    arr[xi, yi] = COLOR

    del arr
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit(0)
