## PURPOSE: Get segments from the MIDI files
## FOR USE: model_training.py

## import necessary libraries 
import os
import random
import midi
import numpy as np
import piece_parser

segment_length = 128
divison_length = 16

l_bound = 24
u_bound = 102

def get_pieces(path):
    pieces = {}

    for file in os.listdir(path):
        file_name = file[:-4]
        extension = file[-4:]

        if extension.lower() != '.midi':
            continue

        file_path = os.path.join(path, file)
        piece = get_piece(file_path)

        if len(piece) < segment_length:
            continue

        pieces[file_name] = piece

    return pieces

def get_segment(pieces):
    selected_pieces = random.choice(pieces.values())

    start_index = random.randrange(0, len(selected_pieces) - segment_length, divison_length)
    end_index = start_index + segment_length

    output = selected_pieces[start_index:end_index]
    input = data_parser.get_multiple_input_forms(output)

    return input, output

def get_piece_batch(pieces, batch_size):
    inputs, outputs = zip(*[get_segment(pieces) for _ in range(batch_size)])
    return np.array(inputs), np.array(outputs)

def get_piece(midi_file):
    pattern = midi.read_midifile(midi_file)

    remaining_time = [track[0].tick for track in pattern]

    positions = [0 for _ in pattern]

    time = 0
    span = u_bound - l_bound

    state_matrix = []
    state = [[0, 0] for _ in xrange(span)]
    state_matrix.append(state)

    while True:
        if time % (pattern.resolution / 4) == (pattern.resolution / 8):
            old_state = state

            state = [[old_state[x][0], 0] for x in xrange(span)]
            state_matrix.append(state)

        for i in xrange(len(remaining_time)):
            while remaining_time[i] == 0:
                track = pattern[i]
                position = positions[i]

                event = track[position]
                if isinstance(event, midi.NoteEvent):
                    if (event.pitch < l_bound) or (event.pitch >= u_bound):
                        pass
                        # print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
                    else:
                        if isinstance(event, midi.NoteOffEvent) or event.velocity == 0:
                            state[event.pitch - LOWER_BOUND] = [0, 0]
                        else:
                            state[event.pitch - LOWER_BOUND] = [1, 1]
                elif isinstance(event, midi.TimeSignatureEvent):
                    if event.numerator not in (2, 4):
                        return state_matrix

                try:
                    remaining_time[i] = track[position + 1].tick
                    positions[i] += 1
                except IndexError:
                    remaining_time[i] = None

            if remaining_time[i] is not None:
                remaining_time[i] -= 1

        if all(t is None for t in remaining_time):
            break

        time += 1

    return state_matrix

def save_piece(piece, file_path):
    piece = np.asarray(piece)

    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)

    span = u_bound - l_bound
    tickscale = 55

    lastcmdtime = 0
    prevstate = [[0, 0] for x in range(span)]
    for time, state in enumerate(piece + [prevstate[:]]):
        offNotes = []
        onNotes = []
        for i in range(span):
            n = state[i]
            p = prevstate[i]
            if p[0] == 1:
                if n[0] == 0:
                    offNotes.append(i)
                elif n[1] == 1:
                    offNotes.append(i)
                    onNotes.append(i)
            elif n[0] == 1:
                onNotes.append(i)
        for note in offNotes:
            track.append(midi.NoteOffEvent(tick=(time - lastcmdtime) * tickscale, pitch=note + l_bound))
            lastcmdtime = time
        for note in onNotes:
            track.append(midi.NoteOnEvent(tick=(time - lastcmdtime) * tickscale, velocity=40, pitch=note + l_bound))
            lastcmdtime = time

        prevstate = state

    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

    midi.write_midifile(file_path, pattern)
