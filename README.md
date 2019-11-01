# Music Net

Note: This project was made for the purpose of my learning experience and is not intended to actually be used

## Summary

The goal of this network is to generate music using the MIDI format.

This project uses C++ for preprocessing the MIDI files to save time (because Python is super slow at converting files). It uses external code to format the file found here: https://github.com/craigsapp/midifile.git

This network uses a simple double layered recurrent network (GRU) to predict the next note in a certain sequence. This network attempts to solve a classification problem, as the sequence of notes and rests are provided as one-hot encodings. For the final output layer, the softmax activation is used, with categorical_crossentropy, and the RMSProp optimizer. The results of this network are mediocre, and definitely can be improved on.
At the moment, I am working on a different network to attempt to generate better sounding music. This new network will use a RL-GAN where the policy network acts as the generator, the discriminator provides the rewards, the action taken by the policy network is the next note in the sequence, the state is the past notes in the sequence. I am very unsure if this will work, but I have yet to try...
