import tkinter as tk
import random

class WaterDropGameModel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.score = 0
        self.high_score = 0
        self.cup_width = 100
        self.cup_speed = 10
        self.cup_x = self.width // 2
        self.droplets = []
        self.danger_drops = []
        self.game_over = False
        self.droplet_speed = 5  # Initial droplet falling speed
        self.droplet_acceleration = 1.01  # Acceleration factor for increasing droplet speed

    def update_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score

    def move_cup_left(self):
        if not self.game_over and self.cup_x - self.cup_width // 2 > 0:
            self.cup_x -= self.cup_speed

    def move_cup_right(self):
        if not self.game_over and self.cup_x + self.cup_width // 2 < self.width:
            self.cup_x += self.cup_speed

    def reset(self):
        self.score = 0
        self.game_over = False
        self.droplets = []
        self.danger_drops = []
        self.droplet_speed = 5  # Reset droplet falling speed

    def increase_difficulty(self):
        self.droplet_speed *= self.droplet_acceleration  # Increase droplet speed

class WaterDropGameView(tk.Tk):
    def __init__(self, model):
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
        self.bind("<Left>", self.move_cup_left)
        self.bind("<Right>", self.move_cup_right)
        self.draw_cup()

    def restart_game(self):
        self.model.reset()
        self.score_label.config(text=f"Score: {self.model.score}")
        self.high_score_label.config(text=f"High Score: {self.model.high_score}")
        self.canvas.delete("all")
        self.retry_button.place_forget()
        self.quit_button.place_forget()
        self.game_over_label.place_forget()
        self.draw_cup()

    def quit_game(self):
        self.quit_button.destroy()
        self.quit()



    def move_cup_left(self, event):
        self.model.move_cup_left()
        self.update_cup_position()

    def move_cup_right(self, event):
        self.model.move_cup_right()
        self.update_cup_position()

    def draw_cup(self):
        self.cup = self.canvas.create_rectangle(self.model.cup_x - self.model.cup_width//2, self.model.height - 20,
                                                self.model.cup_x + self.model.cup_width//2, self.model.height, fill="blue")

    def update_cup_position(self):
        self.canvas.coords(self.cup, self.model.cup_x - self.model.cup_width//2, self.model.height - 20,
                            self.model.cup_x + self.model.cup_width//2, self.model.height)

class WaterDropGameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.spawn_droplet()

    def spawn_droplet(self):
      if not self.model.game_over:
          self.model.increase_difficulty()  # Increase difficulty
          x = random.randint(50, 750)
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
          droplet = self.view.canvas.create_oval(x, y, x + droplet_size, y + droplet_size, fill=droplet_color)
          self.move_droplet(droplet, droplet_speed, points)
      self.view.after(1000, self.spawn_droplet)  # Call spawn_droplet again after 1000 milliseconds

    def move_droplet(self, droplet, droplet_speed, points):
        if droplet in self.view.canvas.find_all():
            self.view.canvas.move(droplet, 0, droplet_speed)
            if self.view.canvas.coords(droplet)[1] >= self.model.height - 20 and self.model.cup_x - self.model.cup_width // 2 <= self.view.canvas.coords(droplet)[0] <= self.model.cup_x + self.model.cup_width // 2:
                self.view.canvas.delete(droplet)
                self.model.update_score(points)
                self.view.score_label.config(text=f"Score: {self.model.score}")
            elif self.view.canvas.coords(droplet)[1] >= self.model.height:
                self.spawn_danger_drop()
            else:
                self.view.after(50, self.move_droplet, droplet, droplet_speed, points)

    def spawn_danger_drop(self):
        if not self.model.game_over:
            x = random.randint(50, 750)
            y = 0
            danger_drop = self.view.canvas.create_oval(x, y, x + 30, y + 30, fill="red")
            self.move_danger_drop(danger_drop)

    def move_danger_drop(self, danger_drop):
        if danger_drop in self.view.canvas.find_all():
            self.view.canvas.move(danger_drop, 0, 2 * self.model.droplet_speed)  # Danger drops move twice as fast
            if self.view.canvas.coords(danger_drop)[1] >= self.model.height - 20 and self.model.cup_x - self.model.cup_width // 2 <= self.view.canvas.coords(danger_drop)[0] <= self.model.cup_x + self.model.cup_width // 2:
                self.end_game()
            elif self.view.canvas.coords(danger_drop)[1] >= self.model.height:
                self.view.canvas.delete(danger_drop)
            else:
                self.view.after(50, self.move_danger_drop, danger_drop)



    def end_game(self):
      self.model.game_over = True
      self.view.game_over_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
      self.view.retry_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
      self.view.quit_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)


if __name__ == "__main__":
    model = WaterDropGameModel(800, 600)
    view = WaterDropGameView(model)
    controller = WaterDropGameController(model, view)
    view.mainloop()
