## PURPOSE: Training the model to output music

import argparse
import numpy as np
import cPickle as pickle
import piece_handler
from generation import MusicGenerator

time_layers = [300, 300]
note_layers = [100, 50]

summary_threshold = 5
checkpoint_threshold = 5

epochs = 2000 
batch_size = 5

config_dir = 'configurations/'
generated_dir = 'generated_pieces/'

config_file_name = 'configuration-%s.config'
generated_piece_name = 'generated-piece-%s.mid'

def display_summary(epoch, batch_size, loss):
    print 'Epoch %d' % epoch
    print '    Loss = %d' % loss
    print '    Pieces = %d' % (epoch * batch_size)


def save_configuration(deep_jammer, tag):
    configuration_path = config_dir + config_file_name % tag
    configuration_file = open(configuration_path, 'wb')
    pickle.dump(deep_jammer.configuration, configuration_file)


def save_loss_history(loss_history):
    f = open(LOSS_HISTORY_FILE_NAME, 'w')
    for loss in loss_history:
        f.write('%s\n' % loss)


def save_generated_piece(generated_piece, tag):
    generated_piece_path = generated_dir + generated_piece_name % tag
    piece_handler.save_piece(generated_piece, generated_piece_path)


def generate_piece(deep_jammer, pieces):
    training_example, label = map(np.array, piece_handler.get_segment(pieces))

    initial_note = training_example[0]
    generated_piece = deep_jammer.predict(piece_handler.SEGMENT_LENGTH, initial_note)

    initial_prediction = np.expand_dims(label[0], 0)
    return np.concatenate((initial_prediction, generated_piece), axis=0)


def train(deep_jammer, pieces, epochs, batch_size):
    loss_history = []

    for epoch in xrange(epochs):
        loss = deep_jammer.update(*piece_handler.get_piece_batch(pieces, batch_size))

        loss_history.append(loss)

        if epoch % SUMMARY_THRESHOLD == 0:
            display_summary(epoch, batch_size, loss)

        if epoch % CHECKPOINT_THRESHOLD == 0:
            print 'Epoch %d -> Checkpoint' % epoch
            save_configuration(deep_jammer, epoch)
            save_loss_history(loss_history)

            piece = generate_piece(deep_jammer, pieces)
            save_generated_piece(piece, epoch)


def main():
    print 'Retrieving Repository...'
    pieces = repository_handler.load_repository(args.repository)

    print 'Generating Pieces'
    deep_jammer = MusicGenerator(time_layers, note_layers)

    print 'Training Model'
    train(deep_jammer, pieces, args.epochs, args.batch_size)

    print 'Saving Configurations'
    save_configuration(deep_jammer, 'final')

    print 'Completing Process...'
    generated_piece = generate_piece(deep_jammer, pieces)
    save_generated_piece(generated_piece, 'final')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Builds a creative, ingenious, classical music generator.')
    parser.add_argument('repository', metavar = 'repository', help = 'the name of the repository')
    parser.add_argument('--epochs', default = epochs, type=int, metavar='epochs', help='the number of epochs')
    parser.add_argument('--batch_size', default = batch_size, type=int, metavar='batch_size', help='the size of each batch')

    args = parser.parse_args()

    main()
