from turtle import Turtle


class Score(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color('white')
        self.penup()
        self.goto(0,270)
        self.headline()

    def headline(self):
        self.write(f"Score: {self.score}", False, "center", 10)

    def game_over(self):
        self.goto(0,0)
        self.write(f"Game Over!", False, "center", 40)

    def increase_score(self):
        self.score += 1
        self.clear()
        self.headline()