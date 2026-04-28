
from py4godot.methods import private
from py4godot.signals import signal, SignalArg
from py4godot.classes import gdclass
from py4godot.classes.core import Vector3
from py4godot.classes.Node2D import Node2D

import threading

import argparse
import collections

import gymnasium as gym
import numpy as np
import torch

import pickle

import npfl139
npfl139.require_version("2526.4")

parser = argparse.ArgumentParser()
# These arguments will be set appropriately by ReCodEx, even if you change them.
parser.add_argument("--recodex", default=False, action="store_true", help="Running in ReCodEx")
parser.add_argument("--render_each", default=0, type=int, help="Render some episodes.")
parser.add_argument("--seed", default=42, type=int, help="Random seed.")
parser.add_argument("--threads", default=1, type=int, help="Maximum number of threads to use.")
# For these and any other arguments you add, ReCodEx will keep your default value.
parser.add_argument("--batch_size", default=32, type=int, help="Batch size.")
parser.add_argument("--epsilon", default=0.1, type=float, help="Exploration factor.")
parser.add_argument("--epsilon_final", default=0.1, type=float, help="Final exploration factor.")
parser.add_argument("--epsilon_final_at", default=1000, type=int, help="Training episodes.")
parser.add_argument("--gamma", default=0.99, type=float, help="Discounting factor.")
parser.add_argument("--hidden_layer_size", default=36, type=int, help="Size of hidden layer.")
parser.add_argument("--learning_rate", default=0.001, type=float, help="Learning rate.")
parser.add_argument("--target_update_freq", default=10, type=int, help="Target update frequency.")
parser.add_argument("--min_memory_count", default=1000, type=int, help="Number of memories required before we start training.")
parser.add_argument("--eval_freq", default=100, type=int, help="Number of memories required before we start training.")


class Network:
	device = torch.device("cpu")
	# Use the following line instead to use GPU if available.
	# device = torch.device(torch.accelerator.current_accelerator() if torch.accelerator.is_available() else "cpu")

	def __init__(self, env: npfl139.EvaluationEnv, args: argparse.Namespace) -> None:
		# TODO: Create a suitable model and store it as `self._model`.
		self._model = torch.nn.Sequential(
			torch.nn.Linear(in_features=env.observation_space.shape[0],  out_features=args.hidden_layer_size),
			torch.nn.ReLU(),
			torch.nn.Linear(in_features=args.hidden_layer_size,  out_features=env.action_space.n),
		).to(self.device)

		# TODO: Define a suitable optimizer from `torch.optim`.
		self._optimizer = torch.optim.AdamW(self._model.parameters(),lr = args.learning_rate)

		# TODO: Define the loss (most likely some `torch.nn.*Loss`).
		self._loss = torch.nn.MSELoss()

	# Define a training method. Generally you have two possibilities
	# - pass new q_values of all actions for a given state; all but one are the same as before
	# - pass only one new q_value for a given state, and include the index of the action to which
	#   the new q_value belongs
	# The code below implements the first option, but you can change it if you want.
	#
	# The `npfl139.typed_torch_function` automatically converts input arguments
	# to PyTorch tensors of given type, and converts the result to a NumPy array.
	@npfl139.typed_torch_function(device, torch.float32, torch.float32)
	def train(self, states: torch.Tensor, q_values: torch.Tensor) -> None:
		self._model.train()
		predictions = self._model(states)
		loss = self._loss(predictions, q_values)
		self._optimizer.zero_grad()
		loss.backward()
		with torch.no_grad():
			self._optimizer.step()

	@npfl139.typed_torch_function(device, torch.float32)
	def predict(self, states: torch.Tensor) -> np.ndarray:
		self._model.eval()
		with torch.no_grad():
			return self._model(states)

	# If you want to use target network, the following method copies weights from
	# a given Network to the current one.
	def copy_weights_from(self, other: "Network") -> None:
		self._model.load_state_dict(other._model.state_dict())


def main(env: npfl139.EvaluationEnv, args: argparse.Namespace) -> None:
	print("Im in main!")
	
	
	
	# Set the random seed and the number of threads.
	npfl139.startup(args.seed, args.threads)
	npfl139.global_keras_initializers()  # Use Keras-style Xavier parameter initialization.
	generator = np.random.RandomState(args.seed)
	
	# Construct the network
	network = Network(env, args)
	network_eval = Network(env, args)
	network_eval.copy_weights_from(network)
	
	# Replay memory; the `max_length` parameter is its maximum capacity.
	replay_buffer = npfl139.ReplayBuffer(max_length=1_000_000)
	Transition = collections.namedtuple("Transition", ["state", "action", "reward", "done", "next_state"])
	
	epsilon = args.epsilon
	training = True
	episode_count = 0
	while training and not args.recodex:
		# Perform episode
		state, done = env.reset()[0], False
		while not done:
			# TODO: Choose an action.
			# You can compute the q_values of a given state by
			#   q_values = network.predict(state[np.newaxis])[0]
			action = np.argmax(network.predict(state[np.newaxis])[0])
			if generator.rand() <= epsilon:
				action = env.action_space.sample()

			next_state, reward, terminated, truncated, _ = env.step(action)
			done = terminated or truncated

			# Append state, action, reward, done and next_state to replay_buffer
			replay_buffer.append(Transition(state, action, reward, done, next_state))
			
			# TODO: If the `replay_buffer` is large enough, perform training using
			# a batch of `args.batch_size` uniformly randomly chosen transitions.
			#
			# The `replay_buffer` offers a method with signature
			#   sample(self, size, replace=True) -> NamedTuple
			# which returns uniformly selected batch of `size` transitions, either with
			# replacement (which is faster, and hence the default) or without.
			# The returned batch is a `Transition` named tuple, each field being
			# a NumPy array containing a batch of corresponding transition components.

			# After you compute suitable targets, you can train the network by
			#   network.train(...)
			if len(replay_buffer) >= args.min_memory_count:
				batch = replay_buffer.sample(args.batch_size, replace=True)
				states, actions, rewards, dones, next_states = batch.state, batch.action, batch.reward, batch.done, batch.next_state
				x = states
				y = network.predict(states) # current predictions

				done_mask = (dones == False)
				y[range(len(next_states)),actions] = rewards + args.gamma * done_mask * network_eval.predict(next_states)[range(len(next_states)),actions] # desired predictions updated for taken action
				network.train(x,y)

			state = next_state
			

		if episode_count%args.target_update_freq == 0: # we spaw the networks
			network_eval.copy_weights_from(network)
		if episode_count%args.eval_freq == 0: # do a single evaluation
			rewards = []
			for i in range(0,20):
				state, done = env.reset()[0], False
				total_reward = 0
				while not done:
					# TODO: Perform an action.            
					action = np.argmax(network.predict(state[np.newaxis])[0])

					next_state, reward, terminated, truncated, _ = env.step(action)
					done = terminated or truncated 

					total_reward += reward
					state = next_state

				rewards.append(total_reward)

			print(f"Evaluation runs result: {np.mean(rewards)}")
			if np.mean(rewards) > 455:
				training = False
		episode_count+=1

		if args.epsilon_final_at:
			epsilon = np.interp(env.episode + 1, [0, args.epsilon_final_at], [args.epsilon, args.epsilon_final])

		# return # ITS HERE JUST TO TEST 1 ITERATION OF THE ALGO
	if args.recodex:
		with open('network', 'rb') as f:
			network = pickle.load(f)
	with open('network', 'wb') as f:
		pickle.dump(network, f)

	# Final evaluation
	while True:
		
		state, done = env.reset(start_evaluation=True)[0], False
		while not done:
			# TODO: Choose a greedy action
			action = np.argmax(network.predict(state[np.newaxis])[0])
			state, reward, terminated, truncated, _ = env.step(action)
			done = terminated or truncated



@gdclass
class RL_QNetwork_Test(Node2D):
		
	def _start_rl_algorithm(self):
		# PUT NEW THREAD HERE
		# THEN IT WILL BE PRINTINTG? MAYBE
		print("Starting")
		main_args = parser.parse_args([] if "__file__" not in globals() else None)
		print(main_args)
		main_env = npfl139.EvaluationEnv(gym.make("CartPole-v1"), main_args.seed, main_args.render_each)
		print("Yiepafuoeba")
		#train_thread:Thread = threading.Thread(target=self._test)
		#train_thread.start()
		
		train_thread:Thread = threading.Thread(target=main, args=(main_env, main_args))
		train_thread.start()
		#self.train_thread.start(main.bind(main_env, main_args))
		#main(main_env, main_args)
	
	def _test(self):
		print("YEaaaa Its wroking")
"""
if __name__ == "__main__":
	main_args = parser.parse_args([] if "__file__" not in globals() else None)

	# Create the environment
	main_env = npfl139.EvaluationEnv(gym.make("CartPole-v1"), main_args.seed, main_args.render_each)

	main(main_env, main_args)
"""
