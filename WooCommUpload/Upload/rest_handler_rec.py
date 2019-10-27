from WooCommUpload.Upload.Model.category import *
from WooCommUpload.Upload.Model.remote_product import *
from WooCommUpload.Upload.woo_api_handler import *
import time

class RestApiHandlerRec:

    def __init__(self):
        self.UPLOAD = False
        self.UPDATE = True
        self.CREATE_CATEGORY_IMAGES = False
        self.UPDATE_CATEGORY_DISPLAY_TYPE = False

        self.CATEGORY_MAX_DEPTH = 3

        self.wooApiHandler = WooApiHandler()
        self.root_category = Category("root", 0)
        self.products_to_be_uploaded = []
        self.products_to_be_updated = []

        self.remote_categories_count = 0
        self.categories_uploaded_count = 0

    def upload_products(self, products):
        self.add_remote_categories()
        self.add_remote_products()

        self.add_local_products(products)
        self.upload_products_to_be_uploaded(self.products_to_be_uploaded)
        self.upload_products_to_be_updated(self.products_to_be_updated)

        if self.CREATE_CATEGORY_IMAGES:
            self.add_category_images()

        if self.UPDATE_CATEGORY_DISPLAY_TYPE:
            self.update_category_display()

    def update_category_display(self):
        """
        Updates the category display settings
        Default | Products | Products + categories etc...
        """

        self.add_remote_categories()

        self.print_title("Updating category display")
        self.update_category_display2(self.root_category, 0)

    def add_remote_categories(self):
        """
        Adds remote categories to the local category/product tree
        """

        self.print_title("Adding remote categories")

        self.add_remote_categories2(self.root_category, 0)

        print("")
        print(str(self.remote_categories_count) + " REMOTE CATEGORIES")
        print("")

    def add_remote_categories2(self, current_category, level):
        """
        Recursive function for add_remote_categories
        """

        sub_categories = self.wooApiHandler.get_sub_categories(current_category.remote_id)

        if len(sub_categories) > 0:
            current_category.sub_categories = sub_categories
            for sub_category in sub_categories:
                self.remote_categories_count += 1
                if level < self.CATEGORY_MAX_DEPTH:
                    self.add_remote_categories2(sub_category, level + 1)

            print(str(self.remote_categories_count) + " REMOTE CATEGORIES")

    def add_remote_products(self):
        """
        Adds remote products to the local category/product tree
        """

        self.print_title("Adding remote products")

        remote_products = self.wooApiHandler.get_products()

        for remote_product in remote_products:

            start = time.time()
            self.add_remote_product(remote_product, self.root_category)
            end = time.time()
            #print("        Time: " + str(end - start))

        self.print_tree()

    def add_remote_product(self, remote_product, current_category):
        """
        Recursive function for add_remote_products
        """

        for subcat in current_category.sub_categories:
            if subcat.remote_id == remote_product.remote_category_id:
                subcat.products.append(remote_product)
                return

        for subcat in current_category.sub_categories:
            self.add_remote_product(remote_product, subcat)

    def add_local_products(self, products):
        """
        Uploads categories to WooCommerce that does not exist on the site.
        Adds products to the products_to_be_uploaded  list that does not exist on site
        """

        self.print_title("Adding local categories")

        for product in products:
            self.add_local_product(product, 0, self.root_category)

        print("")
        print(str(self.categories_uploaded_count) + " CATEGORIES UPLOADED")
        print("")

    def add_local_product(self, product, level, current_category):
        """
        Recursive function that:
        1. Adds the unique categories form the local products to the
        WooCommerce site
        2. Creates a list of products that should be uploaded to the
        WooCommerce site
        3. Compares the WooCommerce products with the local products
        and if there is a difference the product is added to a list
        with the products that should be updated

        Split this function to two separate functions:
        1. One function that adds the unique categories from the
        local products
        2. Another function that adds the products from local
        products
        """

        if level == len(product.categories):
            # PRODUCTS

            curent_remote_product = None
            match = False
            for remote_product in current_category.products:
                if product.supplier_product_id == remote_product.supplier_product_id:
                    curent_remote_product = remote_product
                    match = True

            if self.UPLOAD and not match:
                product.remote_category_id = current_category.remote_id
                self.products_to_be_uploaded.append(product)

            elif self.UPDATE and match:
                # Check difference between local and remote product and add
                # remote product to products_to_be_updated if there is a
                # difference
                if self.compare_products(product, curent_remote_product):
                    curent_remote_product.product_out_price = product.product_out_price
                    curent_remote_product.product_discount_price = product.product_discount_price
                    self.products_to_be_updated.append(curent_remote_product)

        else:
            # CATEGORIES

            match = False
            for subcat in current_category.sub_categories:
                if subcat.name == product.categories[level]:
                    self.add_local_product(product, level + 1, subcat)
                    match = True

            if not match:
                if self.UPLOAD:
                    category_name = product.categories[level]
                    print("")
                    print("Adding " + str(category_name))

                    remote_id = self.wooApiHandler.add_category(
                            category_name,
                            current_category.remote_id)

                    if remote_id:
                        category = Category(category_name, remote_id)
                        current_category.sub_categories.append(category)
                        self.add_local_product(product, level + 1, category)
                        self.categories_uploaded_count += 1

    def compare_products(self, product, remote_product):
        """
        Compares regular price and sale price for the local product and
        the remote product
        """

        product_price = product.product_out_price
        remote_product_price = remote_product.product_out_price

        product_discount_price = product.product_discount_price
        remote_product_discount_price = remote_product.product_discount_price



        print("")
        print("Product price " + product_price)
        print("Remote product price " + remote_product_price)

        print("")
        print("Product discount price " + product_discount_price)
        print("Remote product discount price " + remote_product_discount_price)

        if float(product_price) != float(remote_product_price) or \
                float(product_discount_price) != float(remote_product_discount_price):

            print("--> price difference")
            return True

    def upload_products_to_be_uploaded(self, products):
        """
        Uploads the products form the "products_to_be_uploaded" list
        """

        count = 0
        for product in products:
            count += 1

        print("PRODUCTS TO BE UPLOADED: " + str(count))

        remote_products = self.wooApiHandler.upload_products(products, False)

        count = 0
        for product in remote_products:
            #if product.product_discount_price:
                #print("Product Discount Price " + product.product_discount_price)
            count += 1

        print("PRODUCTS UPLOADED: " + str(count))
        print("")

        for remote_product in remote_products:
            self.add_remote_product(remote_product, self.root_category)

        #self.print_tree()

    def upload_products_to_be_updated(self, products):
        """
        Updates the products form the "products_to_be_updated" list
        """

        count = 0
        for product in products:
            count += 1

        print("PRODUCTS TO BE UPDATED: " + str(count))

        remote_products = self.wooApiHandler.upload_products(products, True)

        count = 0
        for product in remote_products:
            count += 1

        print("PRODUCTS UPDATED: " + str(count))
        print("")

        for remote_product in remote_products:
            self.add_remote_product(remote_product, self.root_category)

        #self.print_tree()

    def add_category_images(self):
        """
        Adds category images dynamically. Takes an image from a product in that category
        """

        self.add_category_images2(self.root_category)

    def add_category_images2(self, current_category):
        """
        Recursive function for add_category_images
        """

        sub_images = []
        current_images = []
        for subcat in current_category.sub_categories:
            sub_images.extend(self.add_category_images2(subcat))

        for product in current_category.products:
            current_images.extend(product.remote_image_ids)

        if current_images:
            self.wooApiHandler.update_category_image(current_category, current_images[0])
        else:
            if sub_images:
                self.wooApiHandler.update_category_image(current_category, sub_images[0])

        return sub_images + current_images

    def update_category_display2(self, current_category, level):
        """
        Recursive function for update_category_display
        """

        self.wooApiHandler.update_category_display(current_category, level)

        for subcat in current_category.sub_categories:
            self.update_category_display2(subcat, level + 1)


    def print_tree(self):
        self.print_title("current tree")
        self.print_tree2(0, self.root_category)

        print("")
        print("----------")

    def print_tree2(self, level, current_category):
        current_category.print_category_short(level)

        if level == 3:
            for product in current_category.products:
                print("                    " + product.product_name)
                #product.print_remote_product()

        for category in current_category.sub_categories:
            self.print_tree2(level + 1, category)

    def delete_all_products(self):
        self.wooApiHandler.delete_all_products()

    def delete_all_categories(self):
        self.wooApiHandler.delete_all_categories()

    def print_title(self, title):
        print("")
        print("----------")
        print("")
        print(title.upper() + ":")
        print("")



