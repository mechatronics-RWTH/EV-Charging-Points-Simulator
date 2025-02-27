import numbers
import pygame 

class ObjectToRender:

    def __init__(self,
                 name: str,
                 screen: pygame.Surface,
                 x_midpoint: int,
                 y_midpoint: int,
                 height: int,
                 width: int,
                 logo: pygame.Surface,
                 soc: numbers.Number =None) -> None:
        self.screen = screen 
        self.name = name
        self.height = height
        self.width = width
        self.set_by_midpoint(x_midpoint, y_midpoint)

        self.soc=soc
        self.logo = pygame.transform.scale(logo,(self.width, self.height))


    def set_by_midpoint(self, x_midpoint, y_midpoint):
        self.x_midpoint: int = x_midpoint
        self.y_midpoint: int = y_midpoint
        self.calculate_coordinates()

    def calculate_coordinates(self):
        self.x_start = self.x_midpoint - self.width/2
        self.x_end = self.x_midpoint + self.width/2
        self.y_start = self.y_midpoint - self.height/2
        self.y_end = self.y_midpoint + self.height/2

    def update_soc(self, soc: numbers.Number):
        self.soc = soc
        grey=(200,200,200)
        pygame.draw.rect(self.screen, grey, (self.x_start+self.width-self.bar_width, self.y_start+self.height-self.bar_height,
                                                self.bar_width, self.bar_height))
        green= (0, 255, 0)
        soc_level=self.bar_height*self.soc
        pygame.draw.rect(self.screen, green, (self.x_start+self.width-self.bar_width, self.y_start+self.height-soc_level,
                                                self.bar_width, soc_level))




    def create(self):

        self.screen.blit(self.logo, (self.x_start, self.y_start))
        if self.soc is not None:
            (self.bar_height, self.bar_width)=(50,20)
            grey=(200,200,200)
            pygame.draw.rect(self.screen, grey, (self.x_start+self.width-self.bar_width, self.y_start+self.height-self.bar_height,
                                                  self.bar_width, self.bar_height))
            green= (0, 255, 0)
            soc_level=self.bar_height*self.soc
            pygame.draw.rect(self.screen, green, (self.x_start+self.width-self.bar_width, self.y_start+self.height-soc_level,
                                                  self.bar_width, soc_level))

   