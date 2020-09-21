class XMLParser:

    def __init__(self, *args, path, **kwargs):
        with open(path, mode="r") as text_file:
            self.text = text_file.read()

    def parseFile(self):
        pass
