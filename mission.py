#!/usr/bin/env python3
"""A file to run the Search and Rescue (SAR) mission scenario.

Robot's mission: Rescue all victims in danger without entering any fire spots and navigate them to the exit. 
"""

import pickle
from time import time, sleep
from environment import Level, Environment
from agent import Agent
import argparse

def run_mission(level):
	global env
	QUIT, PLAYING = 1, 2
	episode = 1
	agent = Agent(level, 1)
	if level == 'easy':
		env = Environment(0)
	elif level == 'hard':
		env = Environment(1)
	else: 
		print("input easy or hard")

	with open("q_table_" + level + ".pkl", "rb") as q_table_file:
		q_table = pickle.load(q_table_file)

	print("Starting Mission...")
	status = PLAYING
	start = time()
	env.reset()
	episode_done = False   

	# get terminal state locations
	exit_map = env.get_exit_position()
	fire_map = env.get_fire_map()      

	# update initial position of robot
	position = tuple(env.current_position) 
	while not episode_done:
		sleep(env.get_speed())
		env.display(episode, episode, q_table)

		# get action to be executed based on q-values
		robot_action = max(q_table[position], key=q_table[position].get)

		# move robot with selected action
		env.move(robot_action)

		# update current position
		position = tuple(env.current_position)
		
		# check if mission is over
		if position in exit_map :
			episode_done = True
		elif position in fire_map :
			episode_done = True

		if not env.update():
			status = QUIT
			break

	if status == PLAYING:
		end = time()
		print(f"Mission Elapsed time: {(end - start)/60} mins")
		while pause(episode, q_table):
			pass
	elif status == QUIT:
		print("Quit mission.")

	return status

def pause(max_episode, q_table):
	global env
	env.display(max_episode, max_episode, q_table)
	return env.update()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Search and Rescue Mission.')
	parser.add_argument('-lv', "--level", choices=['easy', 'hard'], help='Mission level (easy or hard).', required=True)
	args = parser.parse_args()
	run_mission(args.level)



