# -*- coding: utf-8 -*-
from . import merge

def get_hmm():
    """Get a thought."""
    return 'hmmm...'


def hmm():
    """Contemplation..."""
    if merge.extract():
        print(get_hmm())
