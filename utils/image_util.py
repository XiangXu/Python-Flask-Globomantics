from secrets import token_hex
from werkzeug.utils import secure_filename
import datetime, os
from app import app


class ImageUtil(object):

    @staticmethod
    def save_image(image):  
        format = "%Y%m%dT%H%M%S"
        now = datetime.datetime.utcnow().strftime(format)
        random_string = token_hex(2)
        filename = random_string + "_" + now + "_" + image.data.filename
        filename = secure_filename(filename)
        image.data.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
        return filename