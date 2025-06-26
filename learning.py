#!/usr/bin/env python3
"""A file to run the Search and Rescue (SAR) mission learning scenario.

Robot's mission: Rescue all victims in danger without entering any fire spots and navigate them to the exit. 
"""

from agent import Agent
import argparse

def learning(level, max_episode):
    agent = Agent(level, max_episode)
    agent.learn()
    agent.plot()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ELEC ENG 4107 Search and Rescue Mission.')
    parser.add_argument('-lv', "--level", choices=['easy', 'hard'], help='Mission level (easy or hard).', required=True)
    parser.add_argument('-ep', "--episode", help='Number of epsiodes', required=True)
    args = parser.parse_args()
    learning(args.level, args.episode)
