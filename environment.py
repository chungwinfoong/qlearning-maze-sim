#!/usr/bin/env python3
"""Search and Rescue (SAR) mission environment

This module is for creating Search and Rescue (SAR) mission environment. 
"""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg

class Level:
    """Mission level

    This mission includes two levels: EASY and HARD. Based on the level specified, a corresponding map will be generated in the grid world.

    Attributes:
        EASY: A constant which indicates the level EASY.
        HARD: A constant which indicates the level HARD.
        grid_size: Number of grid in the grid world.
        fire_map: Map contains all fire positions.
        girl_map and boy_map: Maps contain all victims positions.
    """
    EASY, HARD = 0, 1
    def __init__(self, level):
        """Initialise map corresponding with the specified level."""
        if level == self.EASY:
            self.grid_size = 4
            self.fire_map = [(0, 2), (0, 3), (1, 0), (3, 2)]
            self.girl_map = [(1, 1)]
            self.boy_map = [(2, 2)]
        elif level == self.HARD:
            self.grid_size = 6
            self.fire_map = [(0, 4), (0, 5), (1, 5), (2, 2), (2, 0),(3, 0), (3, 4), (3, 5), (4, 0), (4, 3), (5, 0)]
            self.girl_map = [(5,2), (0, 2)]
            self.boy_map = [(3, 2), (1, 3)]

    def get_grid_size(self):
        """Get number of grids.

        Returns:
            Number of grids
        """
        return self.grid_size

    def get_map(self):
        """Get map of the grid corresponding with the specified level.
        
        Returns:
            Copies of girl_map, boy_map and fire map
        """
        return self.girl_map.copy(), self.boy_map.copy(), self.fire_map.copy()

class Environment:
    """Mission environment.
    
    In charge of initilisation, displaying and updating the screen. 

    Attributes:
        grid_size: 
            Number of grids.
        window_width:
            window width in px
        window_height: 
            window height in px
        status_font: 
            Font to display mission status.
        q_value_font:
            Font to display Q values.
        screen: 
            Used primarily for initialising screen.
        speed:
            Speed between move. Default: 0.5 second.
        debug_mode:
            If the debug mode is true, all Q values will be displayed on the screen. Otherwise, normal mission screen will be displayed. The debug_mode can be toggled by pressing SPACE on your keyboard.
        scores:
            Mission scores.
        mission_status:
            Either be "Mission Failed!" or "Mission Succeed!".
        robot_status:
            Either be "Rescued Victim", "Exploded", or "Exit Found".
        current_position:
            The robot's current position. It's a list.
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255,0,0)
    FONT_MISSION_STATUS, FONT_MISSION_STATUS_SIZE = 'Arial Bold', 20
    MISSION_CAPTION = 'ELEC ENG 4107 Search and Rescue Mission'
    ACTIONS = {"up": 0, "down": 1, "left": 2, "right": 3}
    FONT_Q_VALUE, FONT_Q_VALUE_SIZE = 'font/cour.ttf', 11
    def __init__(self, level):
        """Init Environment class."""
        self.level = Level(level)
        self.grid_size = self.level.get_grid_size()
        self.window_width = self.grid_size * 100
        self.window_height = self.grid_size * 100 + 100
        self.exit_position = (0, 0)
        pg.init()
        self.status_font = pg.font.SysFont(self.FONT_MISSION_STATUS, self.FONT_MISSION_STATUS_SIZE)
        self.q_value_font = pg.font.SysFont(self.FONT_Q_VALUE, self.FONT_Q_VALUE_SIZE)
        self.q_value_font = pg.font.Font(self.FONT_Q_VALUE, self.FONT_Q_VALUE_SIZE)
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        pg.display.set_caption(self.MISSION_CAPTION)

        self.robot = pg.image.load(r'images/robot.png')
        self.robot = pg.transform.scale(self.robot, (80, 80))
        self.fire = pg.image.load(r'images/wall_fire.png')
        self.fire = pg.transform.scale(self.fire, (80, 85))
        self.exit = pg.image.load(r'images/exitSign.png')
        self.exit = pg.transform.scale(self.exit, (80, 80))
        self.boy1 = pg.image.load(r'images/boy1.png')
        self.boy1 = pg.transform.scale(self.boy1, (80, 80))
        self.girl1 = pg.image.load(r'images/girl1.png')
        self.girl1 = pg.transform.scale(self.girl1, (80, 80))

        self.simple_fire = pg.image.load(r'images/simple_fire.png')
        self.simple_fire = pg.transform.scale(self.simple_fire, (50, 50))
        self.simple_people = pg.image.load(r'images/simple_people.png')
        self.simple_people = pg.transform.scale(self.simple_people, (50, 50))
        self.simple_exit = pg.image.load(r'images/simple_exit.png')
        self.simple_exit = pg.transform.scale(self.simple_exit, (50, 50))
        self.simple_robot = pg.image.load(r'images/simple_robot.png')
        self.simple_robot = pg.transform.scale(self.simple_robot, (50, 50))
        
        self.speed = 0.5
        self.debug_mode = False
        self.reset()
        print("Environment initialised.")

    def reset(self):
        """Reset the environment."""
        self.scores = 0
        self.mission_status = ""
        self.robot_status = ""
        self.girl_map, self.boy_map, self.fire_map = self.level.get_map()
        self.current_position = [self.grid_size - 1, self.grid_size - 1]
    
    def get_speed(self):
        """Get speed between moves.

        Returns:
            Speed value between moves. Note that this value of delay is not a constant. it can be adjusted by pressing the KEYUP/KEYDOWN button.
        """
        return self.speed

    def get_grid_size(self):
        """Get the number of grids."""
        return self.grid_size

    def get_current_position(self):
        """Get robot current position.
        
        Return:
            A tuple of current position.
        """
        return tuple(self.current_position)

    def get_exit_position(self):
        """Get exit position.

        Return:
            A tuple of the exit position.
        """
        return [self.exit_position]

    def get_people_map(self):
        """Get victim map.

        Return:
            List of tuples of all people positions.
        """
        return self.girl_map, self.boy_map

    def get_fire_map(self):
        """Get fire map.

        Return:
            List of tuples of all fire positions.
        """
        return self.fire_map

    def get_actions(self):
        """Get predefined actions.

        Return:
            A dictionary in the format {action_string: action_number}. Example: {"left": 1}.
        """
        return self.ACTIONS

    def get_possible_actions(self, position):
        """Get all possible actions at a position.

        For example: If the robot is at (0, 0), it can not move left or up. Therefore, the possible actions in this case are right and down.

        Args:
            position: Tuple of position.
        
        Return:
            List of all possible actions.
        """
        possible_actions = []
        if position[0] != 0:
            possible_actions.append("up")
        if position[0] != self.grid_size - 1:
            possible_actions.append("down")
        if position[1] != 0:
            possible_actions.append("left")
        if position[1] != self.grid_size - 1:
            possible_actions.append("right")
        return possible_actions

    def to_px(self, position):
        """Convert grid position to pixel.

        Args:
            position: 
                Grid position in tuple/list. Example: (2, 3) or [2, 3].

        Returns:
            A tuple (x, y) coordinates in pixels.
        """
        position = list(position)
        if self.debug_mode:
            px = (position[1] * 100 + 25, position[0] * 100 + 75)
        else:
            px = (position[1] * 100 + 10, position[0] * 100 + 60)
        return px

    def display_layout(self):
        """Display grid layout."""
        # Create grids
        for x in range(0, self.window_width, 100):
            for y in range(50, self.window_height - 50, 100):
                rect = pg.Rect(x, y, x + 100, 100)
                pg.draw.rect(self.screen, self.BLACK, rect, 2)

    def display_debug_mode(self, q_table):
        """Display mission in debug mode.

        Args:
            q_table: The Q table to be displayed. 
            Note that the Q table must be a dictionary with the format of {state: {action: value}}. 
            Example: {(0, 0): {"left": 0.123, ..., "down": 0.456}}.
        """
        for fire_position in self.fire_map:
            self.screen.blit(self.simple_fire, self.to_px(fire_position))
        self.screen.blit(self.simple_exit, self.to_px(self.exit_position))
        self.screen.blit(self.simple_robot, self.to_px(self.current_position))
        for girl_position in self.girl_map:
            self.screen.blit(self.simple_people, self.to_px(girl_position))
        for boy_position in self.boy_map:
            self.screen.blit(self.simple_people, self.to_px(boy_position))
        for position, action_values in q_table.items():
            for action, value in action_values.items():
                q_value = self.q_value_font.render('{:.2f}'.format(value), True, (0, 0, 0))
                if action == "up":
                    self.screen.blit(q_value, (position[1] * 100 + 35, position[0] * 100 + 55))
                elif action == "down":
                    self.screen.blit(q_value, (position[1] * 100 + 35, position[0] * 100 + 135))
                elif action == "left":
                    self.screen.blit(q_value, (position[1] * 100 + 5, position[0] * 100 + 95))
                elif action == "right":
                    self.screen.blit(q_value, (position[1] * 100 + 55, position[0] * 100 + 95))

    def display_mission_mode(self):
        """Display mission in normal mode."""
        for fire_position in self.fire_map:
            self.screen.blit(self.fire, self.to_px(fire_position))
        self.screen.blit(self.exit, self.to_px(self.exit_position))
        self.screen.blit(self.robot, self.to_px(self.current_position))
        for girl_position in self.girl_map:
            self.screen.blit(self.girl1, self.to_px(girl_position))
        for boy_position in self.boy_map:
            self.screen.blit(self.boy1, self.to_px(boy_position))

    def display_info(self, num_episode, max_episode, q_table):
        """Display mission information. 

        Contain: Current episode, Max episode, and Q table in the debug mode.

        Args:
            num_episode: 
                Current episode number to display on the screen.
            max_episode:
                Maximum number of episode to display on the screen.
            q_table: 
                Q table to display on the screen in the debug mode.
        """
        episode = self.status_font.render(f'Episode {num_episode}/{max_episode}', True, (0, 0, 0))
        self.screen.blit(episode, (8, self.window_height - 32))
        speed = self.status_font.render('Speed {:.2f}s'.format(self.speed), True, (0, 0, 0))
        self.screen.blit(speed, (self.window_width - 80, self.window_height - 32))

        scores = self.status_font.render(f'Scores: {self.scores}', True, (0, 0, 0))
        self.screen.blit(scores, (8, 17))
        mission_status = self.status_font.render(f'{self.mission_status}', True, (0, 0, 0))
        self.screen.blit(mission_status, (self.window_width - 120, 17))
        robot_status = self.status_font.render(self.robot_status, True, (0, 0, 0))
        self.screen.blit(robot_status, (self.window_width/2 - 70, 17))

    def display(self, num_episode, max_episode, q_table):
        """Display the mission.

        Args:
            num_episode: 
                Current episode number to display on the screen.
            max_episode:
                Maximum number of episode to display on the screen.
            q_table: 
                Q table to display on the screen in the debug mode.
         """
        self.screen.fill(self.WHITE)
        self.display_layout()

        if self.debug_mode:
            self.display_debug_mode(q_table)
        else:
            self.display_mission_mode()
        self.display_info(num_episode, max_episode, q_table)

    def move(self, action):
        """Move the robot with the specified action.

        Args:
            action:
                A string of action to move the robot. Be either "left", "right", "up", or "down".
        """
        # Display the robot at the grid position
        if action in self.get_possible_actions(self.current_position):
            if action == "up":
                self.current_position[0] -= 1
            elif action == "down":
                self.current_position[0] += 1
            elif action == "left":
                self.current_position[1] -= 1
            elif action == "right":
                self.current_position[1] += 1

    def update(self):
        """Update the mission screen."""
        if tuple(self.current_position) in self.girl_map:
            self.girl_map.remove(tuple(self.current_position))
            self.robot_status = "Rescued Victim"
            self.scores += 1
        elif tuple(self.current_position) in self.boy_map:
            self.boy_map.remove(tuple(self.current_position))
            self.robot_status = "Rescued Victim"
            self.scores += 1
        elif tuple(self.current_position) in self.fire_map:
            self.robot_status = "Robot Exploded"
            self.mission_status = "Mission Failed!"
        elif tuple(self.current_position) == self.exit_position:
            self.robot_status = "Exit Found"
            if self.grid_size == 4 and self.scores == 2 :
                self.mission_status = "Mission Succeed!"
            elif self.grid_size == 6 and self.scores == 4:
                self.mission_status = "Mission Succeed!"  
            else:   
                self.mission_status = "Mission Failed!"

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return False
            if event.type == pg.KEYDOWN:
                # Reduce delay between moves
                if event.key == pg.K_x:
                    if self.speed >= 0.05:
                        self.speed -= 0.05

                # Increase delay between moves
                if event.key == pg.K_w:
                    self.speed += 0.05

                # Toggle displaying Q values
                if event.key == pg.K_SPACE:
                    self.debug_mode ^= True

        pg.display.update()
        return True