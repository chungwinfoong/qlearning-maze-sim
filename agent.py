#!/usr/bin/env python3
"""Q-Learning for solving the Search and Rescued (SAR) mission.
This module implements the intelligence of the main character in the mission. 
"""

import random
import pickle
import numpy as np
from random import choice
from time import time, sleep
from collections import defaultdict
from environment import Level, Environment
import matplotlib.pyplot as plt

ALPHA = 0.7
GAMMA = 0.8
DECAY_RATE = 0.02
EPSILON = 1

BOY_REWARD = 10
GIRL_REWARD = 8
EXIT_REWARD = 5
FIRE_REWARD = -100
EMPTY_REWARD = -1

# Helper function
def smooth(data, window_len=10, window='hanning'):
    """Smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.
    
    Args:
        data: The input signal 
        window_len: The dimension of the smoothing window; should be an odd integer
        window: The type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'. 
        Note that flat window will produce a moving average smoothing.
        
    Example:

        t = linspace(-2,2,0.1)
        data = sin(t) + randn(len(t)) * 0.1
        y = smooth(data)
    
    See also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    NOTE: length(output) != length(input), to correct this: 
            return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if data.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")
    if data.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")
    if window_len < 3:
        return data
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    s = np.r_[data[window_len-1:0:-1], data, data[-2:-window_len-1:-1]]

    # Moving average
    if window == 'flat': 
        w = np.ones(window_len,'d')
    else:
        w = eval('np.'+ window +'(window_len)')

    y = np.convolve(w/w.sum(), s, mode='valid')
    return y

class Agent:
    """Q-Learning agent.
    
    In charge of creating intelligence for the robot to execute the SAR mission.
    Attributes:
        epsilon, alpha, gamma, decay_rate:
            Q-Learning related parameters.
        max_episode:
            Maximum number of episode to learn.
        q_table:
            Q Table for Q-Learning.
        env: 
            Mission environment class instance.
    """      
    def __init__(self, level, max_episode):
        """Initialise Q-Learning params."""
        if level == "easy":
            _level = Level.EASY
        elif level == "hard":
            _level = Level.HARD
        # Default level
        else:
            _level = Level.EASY
        self.env = Environment(_level)
        self.init_params()
        self.init_q_tables()
        self.init_plot_config()
        self.max_episode = int(max_episode)
        # QUIT: Quit the mission without showing figures. 
        # DONE_LEARNING: Done learning, showing figures and Q table.
        self.QUIT, self.DONE_LEARNING = 1, 2
        print("Q-Learning agent initialised.")

    def init_params(self):
        """Initialise Q-Learning parameters.

        This method is required to be filled in.
        """
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.decay_rate = DECAY_RATE
        self.epsilon = EPSILON

    def init_q_tables(self):
        """Initialise Q Table.

        Note:
            For the purpose of displaying Q table, 
            it is required the Q table to be a nested dictionary with the format: {state: {action: q_value}}.
        """
        # Init states with the format (x, y).
        # Example: (0, 1), (0, 1)
        # Note: States must be a list of tuple.
        self.states = []
        self.grid_size = self.env.get_grid_size()
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                self.states.append((x, y))

        # Init Q Table with the format: {state: {action: q_value}}
        # Example: {(0, 0): {"left": 0.123, ..., "up": 0.456}}
        self.q_table = defaultdict(dict) # For current Q-values
        self.q_diff_table = defaultdict(dict) # For difference between new and old Q-tables. You will need it to check if the Q_values converge.
        self.prev_q_table = defaultdict(dict) # For previous Q-values
        self.actions = self.env.get_actions() # Obtaining robot's actions: up, down, right and left

        for state in self.states:
            for action in self.actions.keys():
                self.q_table[state][action] = 0
                self.q_diff_table[state][action] = 0
                self.prev_q_table[state][action] = 0 

    def init_plot_config(self):
        """Initialise variables for plotting figures.
        
        This method is required to be filled in.
        """
        self.accumulated_reward_for_episode = list()

       
    def plot(self):
        """Plot Q-Learning figures as required in the Task 5.

        This method is required to be filled in.
        """        
        plt.figure()
        plt.plot(self.accumulated_reward_for_episode)
        plt.title('Plot of accumulated reward vs episode')
        plt.xlabel('Episode')
        plt.ylabel('Accumulated reward')
        plt.show()
        plt.figure()
        plt.plot(self.accumulated_reward_for_episode)
        plt.title('Plot of smoothened accumulated reward vs episode')
        plt.xlabel('Episode')
        plt.ylabel('Smoothened accumulated reward')
        plt.show()

    def get_action(self, position):
        """Get action depending on exploration or exploitation.

        This method is required to be filled in.

        Args:
            position: A tuple of position to get action.

        Returns:
            A string of action. Either be "left", "right", "up" or "down".
        """
        possible_action = self.env.get_possible_actions(position)

        self.decay_epsilon_greedy()

        if random.uniform(1,0) > self.epsilon:
            # exploit
            print("exploit")
            action = max(self.q_table[position], key=self.q_table[position].get)
        else:
            # explore
            print("explore")
            better_possible_action = [k for k, v in self.q_table[position].items() if v == 0]
            if better_possible_action:
                action = choice(better_possible_action)
            else:
                action = choice(possible_action)
            
        return action


    def get_reward(self, position):
        """Get reward for the selected action.

        This method is required to be filled in.

        Args:
            position: A tuple of position to get action.

        Returns:
            A value of reward at the specified position.
        """
        self.girl_map, self.boy_map = self.env.get_people_map()
        self.exit_map = self.env.get_exit_position()
        self.fire_map = self.env.get_fire_map()

        print(f"current position {position}")

        if position in self.boy_map: # reward for moving to victim on fire
            reward = BOY_REWARD
            self.boy_map = []
            print("             YOU ARE AT BOY")
        elif position in self.girl_map: # reward for moving to victim not on fire
            reward = GIRL_REWARD
            self.girl_map = []
            print("             YOU ARE AT GIRL")
        elif position in self.exit_map: # reward for moving to exit
            reward = EXIT_REWARD
            print("             YOU ARE AT EXIT")
        elif position in self.fire_map: # reward for moving to fire
            reward = FIRE_REWARD
            print("             YOU ARE AT FIRE")
        else: 
            reward = EMPTY_REWARD
            print("             YOU ARE AT EMPTY")

        
        return reward
  
    def get_q_table(self):
        """Get Q table."""
        return self.q_table

    def decay_epsilon_greedy(self):
        """Decay epsilon greedy implementation.

        This method is required to be filled in.
        """
        print(f"epsilon before: {self.epsilon}")
        self.epsilon = (1-self.decay_rate)*self.epsilon
        print(f"epsilon after: {self.epsilon}")

        # implement lower bound to ensure exploration never totally disappear
        if self.epsilon < 0.1:
            self.epsilon = 0.1

    def restart(self, position):
        """Condition to restart the mission."""
        return position == self.env.get_exit_position() or position in self.env.get_fire_map()

    def pause(self):
        """Pause the mission.

        Use primarily for toggling displaying Q values.
        """
        self.env.display(self.count,self.max_episode, self.q_table)
        return self.env.update()

    def save_q_table(self): 
        # Saving learned Q-table to use for executing the SAR mission
        if self.grid_size == 4:
            level = "easy"
        if self.grid_size == 6:
            level = "hard"
        with open("q_table_" + level + ".pkl", "wb") as q_table_file:
            pickle.dump(self.q_table, q_table_file)


    def checking_convergence(self):
        # Checking if the Q-values obtained from learning process converge.
        max_error = 0
        convergence_flag = True
        for state in self.states:
            for value in self.q_diff_table[state].values():
                if abs(value) > max_error:
                    max_error = abs(value)
                if not (value >= -0.1 and value <= 0.1):
                    convergence_flag = False
        print(f"max q state error: {max_error}")
        return convergence_flag          

    def learn(self):
        """The agent uses Q-learning to obtain the policy 
            and check the convergence of Q-values for the optimal policy. 
        
        IMPORTANT: Perform Q value iteration until convergence

        This method is required to be filled in.

        Run the learning process through a number of episodes until Q-values converge 
        and verify that the robot has found an optimal path (with the least number of steps, 
        yet still ensure all victims are rescued and the exit is found) to the exit. 


        Returns:
            DONE_LEARNING: When ran through the input maximum episode OR when obtained the optimal path (i.e. Q-values converge).
            QUIT: When hit close button on the screen.
        """
        print("Learning...")
        check_flag = 0 # For checking the number of convergence of the Q-table. You can either use or ignore it. It depends on how you implement the code to check the convergence.
        status = self.DONE_LEARNING
        self.count = 0 
        start = time()
        self.init_plot_config()
        for episode in range(self.max_episode):
            # Reset the environment before starting a new episode.
            self.env.reset()
            episode_done = False  
            episode_success = False
            self.count += 1

            # initialise optimal path variable to keep track of path used in episode
            optimal_path = list()
            optimal_path.append(tuple(self.env.current_position))

            # initialise variable to keep track of accumulated reward
            accumulated_reward = 0

            while not episode_done:
                sleep(self.env.get_speed())
                self.env.display(episode, self.max_episode, self.q_table)

                # get current position of robot
                current_robot_position = tuple(self.env.current_position)

                # get action to be executed based on current position
                robot_action = self.get_action(current_robot_position)
                print(f"robot action: {robot_action}")

                # move robot with selected action
                self.env.move(robot_action)

                # update current position, reward, accumulated reward and optimal path
                next_robot_position = tuple(self.env.current_position)
                robot_reward = self.get_reward(next_robot_position)
                accumulated_reward = accumulated_reward + robot_reward
                print(f"robot reward: {robot_reward}")
                optimal_path.append(next_robot_position)

                # update cumulative reward and Q-value in selection state
                if next_robot_position in self.exit_map :
                    self.q_table[current_robot_position][robot_action] = (
                    (1-self.alpha) * self.q_table[current_robot_position][robot_action] +
                    self.alpha * (robot_reward))

                    episode_done = True
                    episode_success = True
                    print(f"Episode {self.count} over. Robot reached exit. Optimal path: {optimal_path}")
                
                elif next_robot_position in self.fire_map :
                    self.q_table[current_robot_position][robot_action] = (
                    (1-self.alpha) * self.q_table[current_robot_position][robot_action] +
                    self.alpha * (robot_reward))

                    episode_done = True
                    episode_success = False
                    print(f"Episode {self.count} over. Robot reached fire. Optimal path: {optimal_path}")
                
                else:
                    self.q_table[current_robot_position][robot_action] = (
                    (1-self.alpha) * self.q_table[current_robot_position][robot_action] +
                    self.alpha * (robot_reward + self.gamma * max(list(self.q_table[next_robot_position].values())))
                )

                if not self.env.update():
                    status = self.QUIT
                    break

            # calculate change in q states
            for state in self.states:
                for action in self.actions.keys():
                    self.q_diff_table[state][action] = self.q_table[state][action] - self.prev_q_table[state][action]
            # check for q state convergence
            # note: added episode_success check before checking convergence, i.e. if robot fails and lands on fire, convergence wont be checked
            if self.checking_convergence() and episode_success:
                print("Q states converged")
                break

            # update prev_q_table ready for next episode
            for state in self.states:
                for action in self.actions.keys():
                    self.prev_q_table[state][action] = self.q_table[state][action] 
            
            # update accumulated reward list
            self.accumulated_reward_for_episode.append(accumulated_reward)

        print("q_diff_table: " , self.q_diff_table)        
        # if not hitting close button, then the status will remain as initialised.
        if status == self.DONE_LEARNING:
            end = time()
            print(f"Done learning. Elapsed time: {(end - start)/60} mins")

            # Saving learned Q-table to use for executing the SAR mission 
            self.save_q_table()

            while self.pause():
                pass
        elif status == self.QUIT:
            print("Quit mission.")
            
        return status