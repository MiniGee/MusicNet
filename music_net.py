
from ModelBase.model_base import ModelBase


class MusicNet(ModelBase):

    def __init__(self, name, loader, log_fname = ''):
        super(MusicNet, self).__init__(name, loader, log_fname)