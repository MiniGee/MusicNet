
import numpy as np

from midi_loader import MidiLoader
from music_net import MusicNet


def main():
	loader = MidiLoader('data_bach', 'dat', dtype = np.uint8)
	loader.load(0.1)

	model = MusicNet('music_conv_net', loader)
	model.create()
	model.load(10)
	model.compile()
	# model.train(10, 80, 10)
	model.generate(32, 200)


if __name__ == '__main__':
    main()