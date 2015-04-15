import logging
from nd2reader.service import BaseNd2
from nd2reader.model import Image, ImageSet

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Nd2(BaseNd2):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)

    def get_image(self, time_index, fov, channel_name, z_level):
        image_set_number = self._calculate_image_set_number(time_index, fov, z_level)
        timestamp, raw_image_data = self._reader.get_raw_image_data(image_set_number, self.channel_offset[channel_name])
        return Image(timestamp, raw_image_data, fov, channel_name, z_level, self.height, self.width)

    def __iter__(self):
        """
        Just return every image in order (might not be exactly the order that the images were physically taken, but it will
        be within a few seconds). A better explanation is probably needed here.

        """
        for i in range(self._image_count):
            for fov in range(self.field_of_view_count):
                for z_level in range(self.z_level_count):
                    for channel in self.channels:
                        image = self.get_image(i, fov, channel.name, z_level)
                        if image.is_valid:
                            yield image

    def image_sets(self, field_of_view, time_indices=None, channels=None, z_levels=None):
        """
        Gets all the images for a given field of view and
        """
        timepoint_set = xrange(self.time_index_count) if time_indices is None else time_indices
        channel_set = [channel.name for channel in self.channels] if channels is None else channels
        z_level_set = xrange(self.z_level_count) if z_levels is None else z_levels

        for timepoint in timepoint_set:
            image_set = ImageSet()
            for channel_name in channel_set:
                for z_level in z_level_set:
                    image = self.get_image(timepoint, field_of_view, channel_name, z_level)
                    if image.is_valid:
                        image_set.add(image)
            yield image_set