# Music Net

Note: This project was made for the purpose of my learning experience and is not intended to actually be used

## Summary

The goal of this network is to generate music using the MIDI format.

This project uses C++ for preprocessing the MIDI files to save time (because Python is super slow at converting files). It uses external code to format the file found here: https://github.com/craigsapp/midifile.git

This network uses a simple double layered recurrent network (GRU) to predict the next note in a certain sequence. This network attempts to solve a classification problem, as the sequence of notes and rests are provided as one-hot encodings. For the final output layer, the softmax activation is used, with categorical_crossentropy, and the RMSProp optimizer. The results of this network are mediocre, and definitely can be improved on.
