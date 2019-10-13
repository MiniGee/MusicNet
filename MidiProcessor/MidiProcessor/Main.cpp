#include <iostream>
#include <fstream>
#include <string>

#include <vector>

#include "dirent.h"

#include <MidiFile.h>

typedef unsigned char Uint8;
typedef unsigned int Uint32;

using namespace smf;

///////////////////////////////////////////////////////////////////////////////

void PrintHelp()
{
	std::cout << "Usage:\n\tMidiProcessor [src] [dst]\n";
}

///////////////////////////////////////////////////////////////////////////////

void Search(const char* directory, const char* extension, std::vector<std::string>& files)
{
	DIR* dir = opendir(directory);
	dirent* entry = readdir(dir);

	size_t extLen = strlen(extension);

	// If not entry, end of directories
	while (entry)
	{
		// If file is directory
		if (entry->d_type == DT_DIR)
		{
			std::string name = entry->d_name;

			// If not current or previous directory
			if (name != "." && name != "..")
				// Recursive search
				Search((std::string(directory) + "/" + name).c_str(), extension, files);
		}

		// Else if regular file
		else if (entry->d_type == DT_REG)
		{
			// String for utilities
			std::string name = entry->d_name;

			// If file's last characters are extension
			if (name.find(extension, name.length() - extLen) != std::string::npos)
				// Add file
				files.push_back(std::string(directory) + "/" + name);
		}

		entry = readdir(dir);
	}
}

///////////////////////////////////////////////////////////////////////////////

#define _4 1.0
#define _8 2.0
#define _16 4.0
#define _32 8.0

#define NO_NOTE 0
#define NOTE_ON 1
#define NOTE_OFF 2

std::vector<Uint8> ProcessMidi(const std::string& path)
{
	// Read midi file
	MidiFile file;
	if (!file.read(path))
		return std::vector<Uint8>();

	// Absolute time ticks
	file.makeAbsoluteTicks();

	// Calc time factor
	double factor = _16 / file.getTicksPerQuarterNote();
	Uint32 totalTime = (Uint32)std::round(file.getFileDurationInTicks() * factor) + 1;
	Uint32 numTracks = file.getNumTracks();


	// Create song grid
	std::vector<std::vector<Uint8>> song(totalTime, std::vector<Uint8>(128, NO_NOTE));
	std::vector<bool> hasNotes(totalTime, false);

	Uint32 start = 0;
	bool firstNote = true;

	// Create grid of notes
	for (Uint32 track = 0; track < numTracks; ++track)
	{
		MidiEventList& events = file[track];

		for (Uint32 e = 0; e < events.size(); ++e)
		{
			MidiEvent& event = events[e];
			Uint32 time = (Uint32)std::round(event.tick * factor);

			if (event.isNoteOn())
			{
				if (firstNote)
				{
					start = time;
					firstNote = false;
				}

				song[time][event[1]] = NOTE_ON;
				hasNotes[time] = true;
			}
			else if (event.isNoteOff())
			{
				// song[time][event[1]] = NOTE_OFF;
				// hasNotes[time] = true;
			}
		}
	}


	// Create note stream
	std::vector<Uint8> stream;
	Uint32 lastTime = start;

	for (Uint32 time = start; time < totalTime; ++time)
	{
		if (hasNotes[time])
		{
			if (lastTime != time)
			{
				Uint32 duration = time - lastTime;
				if (duration > 16)
					duration = 16;

				stream.push_back(duration + 89);
			}

			for (Uint32 note = 20; note < 110; ++note)
			{
				if (song[time][note] == NOTE_ON)
					stream.push_back(note - 20);
			}

			lastTime = time;
		}
	}


	return stream;
}

///////////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[])
{
	if (argc != 3)
	{
		PrintHelp();
		return 1;
	}

	std::string src = argv[1];
	std::string dst = argv[2];

	// Get list of files in source folder
	std::vector<std::string> files;
	Search(src.c_str(), ".mid", files);


	// Process all midi files
	for (Uint32 i = 0; i < files.size(); ++i)
	{
		std::string fname = files[i].substr(files[i].find_last_of('/') + 1);
		printf("%-50s -> %05d.dat\n", fname.c_str(), i);

		std::vector<Uint8> stream = ProcessMidi(files[i]);
		if (!stream.size())
		{
			std::printf("Skipping %s\n", fname.c_str());
			continue;
		}


		char outPath[10];
		sprintf(outPath, "%05d.dat", i);
		std::ofstream out(dst + "/" + outPath, std::ios::binary);

		Uint32 size = stream.size();
		out.write((char*)& size, sizeof(Uint32));
		out.write((char*)& stream[0], size);

		out.close();
	}

	return 0;
}