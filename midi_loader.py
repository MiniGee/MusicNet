 
import struct

import numpy as np

from keras.utils.np_utils import to_categorical

from ModelBase.loader_base import LoaderBase


class MidiLoader(LoaderBase):

	def __init__(self, data_dir, data_ext, dtype = np.float32):
		super(MidiLoader, self).__init__(data_dir, data_ext, dtype)

		self._seq_size = 32
		self._num_notes = 90
		self._num_rests = 16


	def _load_file(self, fname):
		with open(fname, 'rb') as f:
			size = struct.unpack('I', f.read(4))[0]
			stream = struct.unpack('B' * size, f.read(size))

			for i in range(len(stream) - self._seq_size - 1):
				self._x_train.append(stream[i : i + self._seq_size + 1])


	def _format_batch(self, idx, data_x, data_y):
		data = data_x[idx]
		data = to_categorical(data, num_classes = self._num_notes + self._num_rests)

		features = data[:, : -1].astype(np.float32)
		labels = data[:, -1].astype(np.float32)

		return (features, labels)