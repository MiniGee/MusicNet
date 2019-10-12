 
import numpy as np

from ModelBase.loader_base import LoaderBase


class MidiLoader(LoaderBase):

    def __init__(self, data_dir, data_ext, dtype = np.float32):
        super(MidiLoader, self).__init__(data_dir, data_ext, dtype)