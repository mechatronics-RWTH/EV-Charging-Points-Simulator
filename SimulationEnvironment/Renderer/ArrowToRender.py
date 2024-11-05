import pygame 
import math 
class ArrowToRender:
    
    def __init__(self,
                 screen,
                 x_midpoint: int=None ,
                 y_midpoint: int=None, 
                 length: int=100,
                 max_length: int = 100,
                 point_direction: str = 'r',
                 arrow_width: int = 30):
        
        self.screen = screen
        self.arrow_head_ratio =0.2
        self.inner_outer_y_ratio = 0.3
        self.length = length
        self.max_length = max_length
        self.arrow_width = arrow_width * length/100
        self.rotation_dict = {'r': 'u', 
                              'l': 'd', 
                              'u': 'l', 
                              'd': 'r'}
        self.arrow_color = (125, 125, 125)
        self.text = None
        self.font = None
        self.text_size = 20
        self.point_direction = point_direction
        self.desired_direction = point_direction
        
        
        if not x_midpoint is None and not y_midpoint is None:
            self.position_by_midpoint(x_midpoint, y_midpoint)
        self.set_pointing_direction(self.desired_direction)

    def set_text(self, text: str):
        self.text = text

    def position_by_midpoint(self,x_midpoint: int, y_midpoint: int):
        self.x_midpoint = x_midpoint
        self.y_midpoint = y_midpoint
        self.x_max_start = self.x_midpoint - self.max_length/2
    
        self.calculate_coordinates()
        self._set_arrow_points()

    def calculate_coordinates(self):
        self.x_start = self.x_midpoint - self.length/2
        self.x_arrow_head_start =  self.x_start +self.length*(1-self.arrow_head_ratio)
        self.x_end = self.x_start + self.length
        self.y_inner_top = self.y_midpoint - self.arrow_width*0.5*self.inner_outer_y_ratio
        self.y_inner_bottom = self.y_midpoint + self.arrow_width*0.5*self.inner_outer_y_ratio
        self.y_outer_top = self.y_midpoint - self.arrow_width*0.5
        self.y_outer_bottom = self.y_midpoint + self.arrow_width*0.5


    def update_length(self,length: int):
        self.length = length
        self.calculate_coordinates()
        self._set_arrow_points()



    def position_by_startpoint(self):
        raise NotImplementedError

    def add_text(self, 
                 text: str, 
                 text_size: int=None,
                 text_color: tuple=(0,0,0)):
        self.text = text
        if text_size is not None:
            self.text_size = text_size

        self.text_color = text_color

        self.font = pygame.font.Font(None, self.text_size)
        self.text_surface = self.font.render(self.text, True, self.text_color)

    def _set_arrow_points(self):

        self.arrow_points = [(self.x_start, self.y_inner_top ), 
                (self.x_arrow_head_start,  self.y_inner_top ), 
                (self.x_arrow_head_start,   self.y_outer_top), 
                (self.x_end, self.y_midpoint), 
                (self.x_arrow_head_start, self.y_outer_bottom ), 
                (self.x_arrow_head_start, self.y_inner_bottom), 
                (self.x_start, self.y_inner_bottom)]
        self.point_direction = 'r'
        self.set_pointing_direction(self.desired_direction)

        

    def set_pointing_direction(self, direction: str):
        self.desired_direction = direction
        
        while self.point_direction != self.desired_direction:
            self._rotate_polygon()
            self.point_direction = self.rotation_dict[self.point_direction]

    def set_text_position(self):
        if self.text is not None:
            if self.point_direction == 'r' or self.point_direction == 'l':
                self.text_position = (self.x_max_start, self.y_midpoint-30)
            else:
                self.text_position = (self.x_midpoint +30, self.y_midpoint)
            

    def _rotate_polygon(self,
                        angle_in_degrees: float = 90):
        """
            Rotates the given polygon which consists of corners represented as (x, y),
            around center_point (origin by default)
            Rotation is counter-clockwise
            Angle is in degrees
        """
        angle_rad = math.radians(angle_in_degrees)
        rotated_points = []
        for x, y in self.arrow_points:
            temp_x = x - self.x_midpoint
            temp_y = y - self.y_midpoint

            rotated_x = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
            rotated_y = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)

            rotated_points.append((rotated_x + self.x_midpoint, rotated_y + self.y_midpoint))
        
        self.arrow_points = rotated_points

    def create(self):
        # draw background rectangle
        pygame.draw.rect(self.screen, (255,255,255), (self.x_midpoint-self.max_length/2, self.y_midpoint-self.max_length/2, self.max_length, self.max_length))
        pygame.draw.rect(self.screen, (255,255,255), (self.text_position[0], self.text_position[1], self.max_length+40, 20))
        # Draw the arrow
        
        try:
            pygame.draw.polygon(self.screen, self.arrow_color, self.arrow_points)
        except Exception as e:
           
            raise e

        if self.text is not None:            
            self.screen.blit(self.text_surface, self.text_position)

    def update(self, length: int):
        self.update_length(length)
        self.set_text_position()
        self.create()