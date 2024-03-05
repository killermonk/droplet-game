from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
import random
from typing import Any, Callable, TypedDict

EventHandler = Callable[[Any], Any]

class KeyboardEventHandler(TypedDict):
    move_left: EventHandler
    move_right: EventHandler
    move_none: EventHandler

class MoveDirection(Enum):
    LEFT = -1
    NONE = 0
    RIGHT = 1

@dataclass
class Coords:
    x: float
    y: float

    @classmethod
    def from_canvas(cls, canvas, item):
        return cls(*canvas.coords(item)[:2])

    @classmethod
    def from_coords(cls, coords):
        return cls(*coords[:2])

class SpriteBase(ABC):
    def __init__(self, canvas: tk.Canvas, coords: Coords, ref: int) -> None:
        super().__init__()
        self.canvas = canvas
        self.coords = coords
        self.ref = ref

    def step(self):
        self._do_step()
        self.coords = Coords.from_canvas(self.canvas, self.ref)

    @abstractmethod
    def _do_step(self) -> None:
        pass

class DropletSprite(SpriteBase):
    def __init__(self, canvas: tk.Canvas, coords: Coords, size: float, color: str, speed: float, points: int) -> None:
        self.droplet = canvas.create_oval(coords.x, coords.y, coords.x + size, coords.y + size, fill=color)
        self.size = size
        self.speed = speed
        self.points = points
        super().__init__(canvas, coords, self.droplet)

    def _do_step(self) -> None:
        self.canvas.move(self.droplet, 0, self.speed)

    def delete(self):
        self.canvas.delete(self.droplet)

class CupSprite(SpriteBase):
    def __init__(self, canvas: tk.Canvas, coords: Coords, width: float, height: float, color: str, speed: float) -> None:
        self.cup = canvas.create_rectangle(coords.x, coords.y, coords.x + width, coords.y - height, fill=color)
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = MoveDirection.NONE
        super().__init__(canvas, coords, self.cup)

    def _do_step(self) -> None:
        if self.direction == MoveDirection.LEFT and self.coords.x > 0:
            self.canvas.move(self.cup, -self.speed, 0)
        elif self.direction == MoveDirection.RIGHT and self.coords.x + self.width < self.canvas.winfo_width():
            self.canvas.move(self.cup, self.speed, 0)

    def set_move_direction(self, direction: MoveDirection):
        self.direction = direction

    def delete(self):
        self.canvas.delete(self.cup)

class KeyboardControl:
    def __init__(self, view: tk.Tk) -> None:
        self.view = view
        self.events: dict[str, bool] = {}

        self.view.bind('<KeyPress>', self.handle_key_press)
        self.view.bind('<KeyRelease>', self.handle_key_release)

    def get(self, key: str) -> bool:
        return self.events.get(key, False)

    def delete(self):
        self.view.unbind_all("<KeyPress>")
        self.view.unbind_all("<KeyRelease>")
        self.events = {}

    def handle_key_press(self, event: tk.Event):
        self.events[event.keysym] = True

    def handle_key_release(self, event: tk.Event):
        self.events[event.keysym] = False

class WaterDropGameModel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.score = 0
        self.high_score = 0
        self.cup_width = 100
        self.cup_speed = 10
        self.game_over = False
        self.droplet_speed = 5  # Initial droplet falling speed
        self.droplet_acceleration = 1.01  # Acceleration factor for increasing droplet speed

    def update_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score

    def reset(self):
        self.score = 0
        self.game_over = False
        self.droplet_speed = 5  # Reset droplet falling speed

    def increase_difficulty(self):
        self.droplet_speed *= self.droplet_acceleration  # Increase droplet speed

class WaterDropGameView(tk.Tk):
    def __init__(self, model: WaterDropGameModel, on_restart: Callable):
        super().__init__()
        self.model = model
        self.title("Water Drop Game")
        self.geometry(f"{self.model.width}x{self.model.height}")
        self.resizable(False, False)
        self.canvas = tk.Canvas(self, width=self.model.width, height=self.model.height, bg="white")
        self.canvas.pack()
        self.score_label = tk.Label(self, text=f"Score: {self.model.score}", font=("Arial", 16))
        self.score_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        self.high_score_label = tk.Label(self, text=f"High Score: {self.model.high_score}", font=("Arial", 16))
        self.high_score_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.game_over_label = tk.Label(self, text="Game Over", font=("Arial", 36), fg="red")
        self.retry_button = tk.Button(self, text="Retry", command=self.restart_game)
        self.quit_button = tk.Button(self, text="Quit", command=self.quit_game)
        self.on_restart = on_restart

        self.droplets = []
        self.danger_drops = []
        self._init_cup()

    def _init_cup(self):
        self.cup = CupSprite(
            self.canvas,
            Coords(self.model.width / 2 - self.model.cup_width / 2, self.model.height),
            self.model.cup_width,
            20,
            "blue",
            self.model.cup_speed
        )

    def restart_game(self):
        self.model.reset()
        self.score_label.config(text=f"Score: {self.model.score}")
        self.high_score_label.config(text=f"High Score: {self.model.high_score}")
        self.canvas.delete("all")
        self.retry_button.place_forget()
        self.quit_button.place_forget()
        self.game_over_label.place_forget()
        self.droplets = []
        self.danger_drops = []
        self._init_cup()
        self.on_restart()

    def update_score(self):
        self.score_label.config(text=f"Score: {self.model.score}")

    def create_droplet(self, x: float, y: float, size: float, color: str, speed: float, points: int):
        droplet = DropletSprite(self.canvas, Coords(x, y), size, color, speed, points)
        self.droplets.append(droplet)

    def create_danger_droplet(self, x: float, y: float, size: float, color: str, speed: float):
        danger_drop = DropletSprite(self.canvas, Coords(x, y), size, color, speed, -100)
        self.danger_drops.append(danger_drop)

    def quit_game(self):
        self.quit_button.destroy()
        self.quit()

class WaterDropGameController:
    def __init__(self, width: int, height: int):
        self.model = WaterDropGameModel(width, height)
        self.view = WaterDropGameView(self.model, on_restart=self._reset_timers)
        self.spawn_timeout = 1000
        self.move_droplet_timeout = 50
        self.keyboard_repeat = 50
        self.keyboard_control = KeyboardControl(self.view)
        self._reset_timers()

    def _reset_timers(self):
        self.view.after(0, self.spawn_droplet)
        self.view.after(0, self.move_droplets)
        self.view.after(0, self.handle_keyboard)

    def spawn_droplet(self):
        if not self.model.game_over:
            self.model.increase_difficulty()  # Increase difficulty
            x = random.randint(50, self.model.width - 50)
            y = 0
            if random.random() < 0.05:
                droplet_size = 20
                droplet_color = "gold"
                points = 50
                droplet_speed = self.model.droplet_speed * 1.5  # Rare drops move 1.5 times faster
            else:
                droplet_size = 10
                droplet_color = "blue"
                points = 10
                droplet_speed = self.model.droplet_speed

            self.view.create_droplet(x, y, droplet_size, droplet_color, droplet_speed, points)
            self.view.after(self.spawn_timeout, self.spawn_droplet)

    def spawn_danger_drop(self):
        if not self.model.game_over:
            x = random.randint(50, 750)
            y = 0
            self.view.create_danger_droplet(x, y, 30, "red", self.model.droplet_speed * 2)

    def did_droplet_hit_cup(self, droplet: DropletSprite) -> bool:
        droplet_bottom = droplet.coords.y + droplet.size/2
        droplet_left = droplet.coords.x
        droplet_right = droplet.coords.x + droplet.size

        cup_top = self.view.cup.coords.y - self.view.cup.height
        cup_left = self.view.cup.coords.x
        cup_right = self.view.cup.coords.x + self.view.cup.width

        return droplet_bottom > cup_top and droplet_left < cup_right and droplet_right > cup_left

    def move_droplets(self):
        if not self.model.game_over:
            next_droplets = []
            for droplet in self.view.droplets:
                droplet.step()
                # hits bottom
                if droplet.coords.y >= self.model.height:
                    # Let the next frame render before deleting the droplet
                    self.view.after(self.move_droplet_timeout, droplet.delete)
                    self.spawn_danger_drop()
                # hits cup
                elif self.did_droplet_hit_cup(droplet):
                    # Let the next frame render before deleting the droplet
                    self.view.after(self.move_droplet_timeout, droplet.delete)
                    self.model.update_score(droplet.points)
                    self.view.update_score()
                # still in the game
                else:
                    next_droplets.append(droplet)

            # Make sure to update the droplets list after the loop
            self.view.droplets = next_droplets

            next_danger_droplets = []
            for danger_drop in self.view.danger_drops:
                danger_drop.step()
                # hits bottom
                if danger_drop.coords.y >= self.model.height:
                    danger_drop.delete()
                # hits cup
                elif self.did_droplet_hit_cup(danger_drop):
                    self.end_game()
                # still in the game
                else:
                    next_danger_droplets.append(danger_drop)

            # Make sure to update the danger_droplets list after the loop
            self.view.danger_drops = next_danger_droplets

            self.view.after(self.move_droplet_timeout, self.move_droplets)

    def handle_keyboard(self):
        if not self.model.game_over:
            left_down = self.keyboard_control.get("Left")
            right_down = self.keyboard_control.get("Right")
            if left_down ^ right_down: # one or the other, but not both
                if left_down:
                    self.view.cup.set_move_direction(MoveDirection.LEFT)
                else:
                    self.view.cup.set_move_direction(MoveDirection.RIGHT)
            else:
                self.view.cup.set_move_direction(MoveDirection.NONE)
            self.view.cup.step()
            self.view.after(self.keyboard_repeat, self.handle_keyboard)

    def start_game(self):
        self.view.mainloop()

    def end_game(self):
      self.model.game_over = True
      self.view.game_over_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
      self.view.retry_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
      self.view.quit_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)


if __name__ == "__main__":
    controller = WaterDropGameController(800, 600)
    controller.start_game()
