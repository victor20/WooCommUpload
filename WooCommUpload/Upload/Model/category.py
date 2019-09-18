class Category:

    def __init__(self, name, remote_id):
        self.name = name
        self.remote_id = remote_id
        self.sub_categories = []
        self.products = []
        self.parent_remote_id = None

    def print_category(self, level):
        print("")
        print("    " * (level + 1) + "Name: " + self.name)
        print("    " * (level + 1) + "Remote Id: " + str(self.remote_id))
        print("    " * (level + 1) + "Parent Remote Id: " + str(self.parent_remote_id))

    def print_category_short(self, level):
        print("    " * (level + 1) + self.name + " " + str(self.remote_id))


