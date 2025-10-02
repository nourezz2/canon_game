import random
import json
from math import cos, sin, radians
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout

# Define global variables for game state
score = 0
game_over = False
level = 1

class CannonGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.help_label = Label(text="", pos=(Window.width/2, Window.height/2), size_hint=(None, None))
        self.add_widget(self.help_label)
        self.help_clicked = False
        help_button = Button(text='Help', pos=(Window.width / 2 - 400, Window.height - 100))
        help_button.bind(on_release=self.show_help)
        self.add_widget(help_button)

        save_button = Button(text='Save', pos=(Window.width / 2 - 200, Window.height - 100))
        save_button.bind(on_release=self.save_game)
        self.add_widget(save_button)

        load_button = Button(text='Load', pos=(Window.width / 2 + 100, Window.height - 100))
        load_button.bind(on_release=self.load_game)
        self.add_widget(load_button)

        reset_button = Button(text='reset', pos=(Window.width / 2 +200, Window.height - 100))
        reset_button.bind(on_release=self.reset_game)
        self.add_widget(reset_button)
        
        self.canvas.add(Color(0, 0, 1, 1))  # Blue color for cannon
        self.cannon = Rectangle(pos=(40, 40), size=(40, 40))
        self.canvas.add(self.cannon)
        
        self.canvas.add(Color(1, 0, 0, 1))  # Red color for bullet
        self.bullet = Rectangle(pos=(60, 60), size=(30, 10))
        self.canvas.add(self.bullet)
        
        self.bullet_state = 'ready'
        self.bullet_speed = 50
        self.bullet_heading = 50
        self.gravity = 1
        self.bullet_dx = self.bullet_speed * cos(radians(self.bullet_heading))
        self.bullet_dy = self.bullet_speed * sin(radians(self.bullet_heading))

        self.enemy_list = []

        self.score_label = Label(text="\nScore: 0", pos=(Window.width / 2 - 50, Window.height - 50), font_size=24)
        self.level_label = Label(text="\nLevel: 1", pos=(Window.width / 2 - 50, Window.height - 100), font_size=24)
        self.add_widget(self.score_label)
        self.add_widget(self.level_label)

        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.update, 1/60)

        self.trajectory_line = Line(points=[], width=2)
        self.canvas.after.add(self.trajectory_line)

    def show_help(self, instance):
        if self.help_clicked:
            self.help_label.text = ""
            self.help_clicked = False
        else:
            self.help_label.text = """
                Welcome to the Game!\n\n
                How to play:\n
                1. Use the LEFT and RIGHT arrow keys to aim and SPACEBAR to fire.\n
                2. Do not let any enemy pass to the left side of the screen. - game over if it happend.\n
                3. Shoot enemies off screen for points - more points as level increases.\n
                4. Every 10th point, the speed of the enemy spawning will increase.
                """
            self.help_clicked = True
            
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 44 and self.bullet_state == 'ready': 
            self.shoot()
        elif keycode ==  80 :
            self.turn_left()
        elif keycode == 79: 
            self.turn_right()

    def shoot(self):
        sound = SoundLoader.load('missile.WAV')
        if sound:
            sound.play()
        self.bullet_state = 'fire'

    def turn_left(self):
        if self.bullet_state == 'ready':
            self.bullet_heading += 5
            self.update_bullet_velocity()
            self.update_trajectory_line()

    def turn_right(self):
        if self.bullet_state == 'ready':
            self.bullet_heading -= 5
            self.update_bullet_velocity()
            self.update_trajectory_line()

    def update_bullet_velocity(self):
        self.bullet_dx = self.bullet_speed * cos(radians(self.bullet_heading))
        self.bullet_dy = self.bullet_speed * sin(radians(self.bullet_heading))

    def update_trajectory_line(self):
        start_x = self.bullet.pos[0] + self.bullet.size[0] / 2
        start_y = self.bullet.pos[1] + self.bullet.size[1] / 2
        end_x = start_x + self.bullet_dx * 10  # Draw the line 10 units ahead
        end_y = start_y + self.bullet_dy * 10
        self.trajectory_line.points = [start_x, start_y, end_x, end_y]

    def update(self, dt):
        global score, game_over, level

        if self.bullet_state == 'fire':
            self.bullet.pos = (self.bullet.pos[0] + self.bullet_dx, self.bullet.pos[1] + self.bullet_dy)
            self.bullet_dy -= self.gravity

            if self.bullet.pos[1] < -30 or self.bullet.pos[0] > Window.width or self.bullet.pos[0] < 0:
                self.reset_bullet()

        if len(self.enemy_list) < 10 + level * 2 and random.random() < 0.05:
            enemy = Ellipse(pos=(Window.width, random.randint(0, Window.height - 50)), size=(50, 50))
            self.canvas.add(Color(random.random(), random.random(), random.random(), 1))
            self.canvas.add(enemy)
            self.enemy_list.append(enemy)

        for enemy in self.enemy_list:
            enemy.pos = (enemy.pos[0] - 0.3 * (1 + 0.1 * level), enemy.pos[1])

            if enemy.pos[0] < -50:
                self.end_game()
            elif self.check_collision(self.bullet, enemy):
                try:
                    self.canvas.remove(enemy)
                    self.enemy_list.remove(enemy)
                    sound = SoundLoader.load('pop.wav')
                    if sound:
                        sound.play()
                    self.reset_bullet()
                    score += 1
                    self.score_label.text = f"\nScore: {score}"
                    if score % 10 == 0:
                        level += 1
                        self.level_label.text = f"\nLevel: {level}"
                except:
                    pass

    def reset_bullet(self):
        self.bullet.pos = (60, 60)
        self.bullet_state = 'ready'
        self.update_bullet_velocity()
        self.trajectory_line.points = []  # Clear the trajectory line

    def end_game(self):
        global game_over
        game_over = True
        self.canvas.clear()
        if self.score_label.parent:
            self.remove_widget(self.score_label)  # Remove the score label from its current parent
        self.score_label.text = f"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nScore: {score}\nGAME OVER"
        self.add_widget(self.score_label)  # Re-add the score label widget to the canvas

    def check_collision(self, bullet, enemy):
        bx, by = bullet.pos
        ex, ey = enemy.pos
        return bx < ex + enemy.size[0] and bx + bullet.size[0] > ex and by < ey + enemy.size[1] and by + bullet.size[1] > ey

    def save_game(self, instance):
        global score, level, game_over
        game_state = {
            "score": score,
            "level": level,
            "game_over": game_over
        }
        try:
            with open('savegame.json', 'w') as file:
                json.dump(game_state, file, indent=4)
            print("Game saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving the game: {e}")

    def load_game(self, instance):
        global score, level, game_over
        try:
            with open('savegame.json', 'r') as file:
                game_state = json.load(file)
            score = game_state["score"]
            level = game_state["level"]
            game_over = game_state["game_over"]
            self.score_label.text = f"\nScore: {score}"
            self.level_label.text = f"\nLevel: {level}"
            print("Game loaded successfully.")
            self.restart_game()
        except FileNotFoundError:
            print("No saved game found.")
        except json.JSONDecodeError:
            print("Error decoding the saved game file.")
        except Exception as e:
            print(f"An error occurred while loading the game: {e}")

    def restart_game(self):
        # Clear all enemies
        for enemy in self.enemy_list:
            self.canvas.remove(enemy)
        self.enemy_list.clear()

        
    def reset_game(self, instance):
        global score , level
        score = 0 
        level = 1
        self.score_label.text = f"\nScore: {score}"
        self.level_label.text = f"\nLevel: {level}"
        # Clear all enemies
        for enemy in self.enemy_list:
            self.canvas.remove(enemy)
        self.enemy_list.clear()

class CannonApp(App):
    def build(self):
        game = CannonGame()
        parent = FloatLayout()
        parent.add_widget(game)
        return parent
    

if __name__ == '__main__':
    CannonApp().run()
