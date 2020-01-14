#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 10/12/2019
           """

import gym
from IPython.display import display
from matplotlib import animation, pyplot


def replay_frames(frames, interval=100):
    """
Displays a list of frames as a gif, with controls
"""
    # pyplot.figure(figsize=(frames[0].shape[1] / 72.0, frames[0].shape[0] / 72.0), dpi = 72)
    patch = pyplot.imshow(frames[0])
    pyplot.axis("off")

    def animate(start_episode):
        patch.set_data(frames[start_episode])

    anim = animation.FuncAnimation(
        pyplot.gcf(), animate, frames=len(frames), interval=interval
    )
    display(anim)


if __name__ == "__main__":

    env = gym.make("Pendulum-v0")
    state = env.reset()

    frames = []
    done = False
    while not done:
        frames.append(env.render(mode="rgb_array"))

        state, reward, done, info = env.step(env.action_space.sample())
    env.close()

    replay_frames(frames)
