
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from midiutil import MIDIFile

from ModelBase.model_base import ModelBase

from keras.models import Model
from keras.layers import Dense, Dropout, Input, Reshape, Flatten
from keras.layers import Conv1D, MaxPool1D, BatchNormalization
from keras.layers import CuDNNGRU, Bidirectional
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import RMSprop
from keras.utils.np_utils import to_categorical


class MusicNet(ModelBase):

	def __init__(self, name, loader, log_fname = ''):
		super(MusicNet, self).__init__(name, loader, log_fname)


	def create(self):
		num_classes = self._loader._num_notes + self._loader._num_rests
		input = Input(shape = (self._loader._seq_size, num_classes))
		
		x = CuDNNGRU(512, return_sequences = True)(input)
		x = Dropout(0.5)(x)
		x = CuDNNGRU(512, return_sequences = False)(x)
		x = Dropout(0.5)(x)

		output = Dense(num_classes, activation = 'softmax')(x)

		self._model = Model(inputs = input, outputs = output)
		self._model.summary()


	def compile(self):
		optimizer = RMSprop(lr = 0.0002)
		self._model.compile(
			optimizer = optimizer,
			loss = 'categorical_crossentropy',
			metrics = ['accuracy']
		)

		self._metrics = ['Loss', 'Accu']


	def generate(self, mb_size, seq_size):

		songs = np.zeros((mb_size, seq_size), dtype = np.uint8)

		batch = self._loader.get_testing_batch(mb_size)[0]

		num_classes = self._loader._num_notes + self._loader._num_rests
		prob_dist = [0.6, 0.9, 1.0]

		# Generate notes
		print('Generating notes...')
		for i in tqdm(range(seq_size)):
			notes = self._model.predict(batch)
			rand = np.random.uniform(size = mb_size)
			result = np.zeros(mb_size, dtype = np.uint8)

			# Choose note based on distribution
			for n in range(len(notes)):
				for p in range(len(prob_dist)):
					note = np.argmax(notes[n])
					notes[n, note] = 0.0
					if rand[n] < prob_dist[p]:
						break

				result[n] = note

			songs[:, i] = result
			result = to_categorical(result, num_classes)

			batch[:, : -1] = batch[:, 1 :]
			batch[:, -1] = np.copy(result)
			
		
		print('Saving songs...')
		for i, song in enumerate(tqdm(songs)):
			midi = MIDIFile(1)
			midi.addTempo(0, 0, 120)
			time = 0

			chord = []

			for note in song:
				if note < 90:
					chord.append(note + 20)
				else:
					duration = note - 89
					for n in chord:
						midi.addNote(0, 0, n, time, duration, 60)

					# Reset chord
					chord = []
					time += duration

			with open(os.path.join('output', '%d.mid' % i), 'wb') as f:
				midi.writeFile(f)