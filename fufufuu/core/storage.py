from django.core.files.storage import FileSystemStorage


class FufufuuStorage(FileSystemStorage):

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(FufufuuStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name
