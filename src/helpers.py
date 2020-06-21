import os
import io
from zipfile import ZipFile

class Zipper:
    
    @staticmethod
    def make_bytes(path):
        buf = io.BytesIO()
        with ZipFile(buf, 'w') as z:
            for full_path, archive_name in Zipper.files_to_zip(path):
                z.write(full_path, archive_name)
        total = buf.getvalue()
        return total
    
    @staticmethod
    def files_to_zip(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                full_path = os.path.join(root, f)
                archive_name = full_path[len(path) + len(os.sep):]
                yield full_path, archive_name