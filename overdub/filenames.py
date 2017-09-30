import os


def make_output_filename(prefix=None):
    if prefix:
        prefix = prefix + '-'
    else:
        prefix = ''

    return os.path.expanduser('~/Desktop/overdub-{}out.wav'.format(prefix))
