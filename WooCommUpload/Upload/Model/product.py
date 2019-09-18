class Product:

    def __init__(self, *, supplier_product_id, product_name):

        self.supplier_product_id = supplier_product_id
        self.product_name = product_name

        self.categories = []
        self.product_in_price = None
        self.product_out_price = None
        self.product_discount_price = None
        self.product_description = ""
        self.product_images = []
        self.product_specification = []
        self.product_eco_labels = []
        self.product_stock = ""
        self.price_quantities = []

        self.remote_category_id = ""
        self.remote_product_id = ""

    def print_product(self):

        print("")
        print("        product: " + self.supplier_product_id)
        print("            cat: " + str(self.categories))
        print("            name: " + self.product_name)
        print("            price: " + str(self.product_in_price))
        print("            desc: " + self.product_description)

        print("            images")
        for product_image in self.product_images:
            print("                " + str(product_image))

        print("            product spec")
        for ps in self.product_specification:
            print("                " + str(ps))

        print("            remote category id: " + str(self.remote_category_id))

    def print_remote_product(self):

        print("")
        print("        product: " + self.supplier_product_id)
        print("            remote product id: " + str(self.remote_product_id))
        print("            remote category id: " + str(self.remote_category_id))


    def print_product_small(self):
        print("    product: " + self.supplier_product_id + " Nr of img: " + str(len(self.product_images)))


    #def print_debug(self):




