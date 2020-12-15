## FUNCTION: Get MIDI files and parse the notes from them for training
## USED: Globally (change_output / piece_handler)

# Import necessary libraries and programs 
import itertools
import piece_handler

# Returns array of notes from MIDI
def get(list, index, default):
    try:
        return list[index]
    except IndexError:
        return default

# Get previous note or "context" of the piece
def get_context(state):
    context = [0] * 12

    for note, feature in enumerate(state):
        if feature[0] == 1:
            pitch = (note + piece_handler.LOWER_BOUND) % 12
            context[pitch] += 1

    return context

# Get the beat (based on length of note)
def get_beat(time):
    return [2 * x - 1 for x in [time % 2, (time // 2) % 2, (time // 4) % 2, (time // 8) % 2]]

# Get input and return the note, state, context, and beat of this notes
def get_input(note, state, context, beat):
    position_component = [note]

    pitch = (note + piece_handler.LOWER_BOUND) % 12
    pitch_component = [int(i == pitch) for i in range(12)]

    note_range = range(-12, 13)
    previous_range_component = list(itertools.chain.from_iterable((get(state, note + offset, [0, 0]) for offset in note_range)))

    context_component = context[pitch:] + context[:pitch]

    return position_component + pitch_component + previous_range_component + context_component + beat + [0]

# Singular note (at the same time)
def get_single_input(state, time):
    return [get_input(note, state, get_context(state), get_beat(time)) for note in range(len(state))]

# Multiple notes (at the same time)
def get_multiple_input(state_matrix):
    return [get_single_input(state, time) for time, state in enumerate(state_matrix)]
