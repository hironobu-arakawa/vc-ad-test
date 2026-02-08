"""Readable, DDD-ish particle demo.

Domain: Particles that move and bounce in a 2D world.
Application: Game loop coordinating update + render.
Infrastructure: Pygame for window + drawing.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, List, Tuple

import pygame


# ----------------------------
# Domain
# ----------------------------


@dataclass(frozen=True)
class Vector2:
    x: float
    y: float

    def add(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def scale(self, factor: float) -> "Vector2":
        return Vector2(self.x * factor, self.y * factor)


@dataclass(frozen=True)
class Bounds:
    width: int
    height: int

    def clamp_and_reflect(self, position: Vector2, velocity: Vector2) -> Tuple[Vector2, Vector2]:
        x, y = position.x, position.y
        vx, vy = velocity.x, velocity.y

        if x < 0:
            x = 0
            vx *= -1
        elif x > self.width - 1:
            x = self.width - 1
            vx *= -1

        if y < 0:
            y = 0
            vy *= -1
        elif y > self.height - 1:
            y = self.height - 1
            vy *= -1

        return Vector2(x, y), Vector2(vx, vy)


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)


@dataclass(frozen=True)
class Particle:
    position: Vector2
    velocity: Vector2
    color: Color

    def step(self, bounds: Bounds) -> "Particle":
        next_pos = self.position.add(self.velocity)
        bounded_pos, bounded_vel = bounds.clamp_and_reflect(next_pos, self.velocity)
        return Particle(bounded_pos, bounded_vel, self.color)


class ParticleSystem:
    def __init__(self, particles: Iterable[Particle], bounds: Bounds) -> None:
        self._particles: List[Particle] = list(particles)
        self._bounds = bounds

    def update(self) -> None:
        self._particles = [p.step(self._bounds) for p in self._particles]

    def particles(self) -> Iterable[Particle]:
        return self._particles


# ----------------------------
# Application
# ----------------------------


class ParticleSimulation:
    def __init__(self, system: ParticleSystem) -> None:
        self._system = system

    def tick(self) -> None:
        self._system.update()

    def particles(self) -> Iterable[Particle]:
        return self._system.particles()


# ----------------------------
# Infrastructure (Pygame)
# ----------------------------


class PygameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

    def clear(self) -> None:
        self._screen.fill((0, 0, 0))

    def draw(self, particles: Iterable[Particle]) -> None:
        for p in particles:
            self._screen.set_at((int(p.position.x), int(p.position.y)), p.color.as_tuple())

    def present(self) -> None:
        pygame.display.flip()


class GameLoop:
    def __init__(self, simulation: ParticleSimulation, renderer: PygameRenderer, fps: int = 60) -> None:
        self._simulation = simulation
        self._renderer = renderer
        self._fps = fps
        self._clock = pygame.time.Clock()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self._simulation.tick()
            self._renderer.clear()
            self._renderer.draw(self._simulation.particles())
            self._renderer.present()
            self._clock.tick(self._fps)


# ----------------------------
# Composition Root
# ----------------------------


def random_particle(bounds: Bounds) -> Particle:
    position = Vector2(random.random() * bounds.width, random.random() * bounds.height)
    velocity = Vector2((random.random() - 0.5) * 4.2, (random.random() - 0.5) * 4.2)
    color = Color(random.randrange(256), random.randrange(256), random.randrange(256))
    return Particle(position, velocity, color)


def build_system(count: int, bounds: Bounds) -> ParticleSystem:
    particles = (random_particle(bounds) for _ in range(count))
    return ParticleSystem(particles, bounds)


def main() -> None:
    pygame.init()
    width, height = 960, 540
    bounds = Bounds(width, height)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Readable Particle Demo (Python)")

    system = build_system(50_000, bounds)
    simulation = ParticleSimulation(system)
    renderer = PygameRenderer(screen)

    GameLoop(simulation, renderer, fps=60).run()
    pygame.quit()


if __name__ == "__main__":
    main()
