from PIL import Image
from zope.interface import implements

from tailor import itailor


class ImageThumb:
    """
    simple thumbnailer.

    spawns a thread that launches a childprocess that resizes the image.
    creates a square crop to the size passed
    """
    implements(itailor.IFileOp)

    def __init__(self, size, destination):
        self.size = size
        self.destination = destination

    def thumbnail(self, filename):
        image = Image.open(filename)
        image.thumbnail(self.size)
        image.save(self.destination)
        return self.destination

    def process(self, filename):
        if filename is None:
            raise ValueError
        return threads.deferToThread(self.thumbnail, filename)


class ImageThumbFactory:
    implements(itailor.iTailorPlugin)
    __plugin__ = ImageThumb

    @classmethod
    def new(cls, *args, **kwargs):
        return cls.__plugin__(*args, **kwargs)


factory = ImageThumbFactory()