from turtle import Turtle
import random

class Food (Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("blue")
        self.penup()
        self.shapesize(0.5, 0.5)
        self.speed('fastest')
        self.refresh()

    def refresh(self):
        random_x = random.randrange(-280, 280, 20)
        random_y = random.randrange(-280, 280, 20)
        self.clear()
        self.goto(random_x,random_y)