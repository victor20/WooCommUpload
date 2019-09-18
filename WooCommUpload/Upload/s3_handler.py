import boto3
from WooCommUpload.Config import cred

class S3Handler:

    def __init__(self):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=cred.aws_access_key_id,
            aws_secret_access_key=cred.aws_secret_access_key,
            region_name=cred.region_name)

        self.bucket = s3.Bucket(cred.bucket_name)

    def get_images(self, supplier_product_id):
        images = []
        objects = list(self.bucket.objects.filter(Prefix=supplier_product_id))
        for object in objects:
            images.append({"src": cred.src + object.key})

        # print("--- TRYING TO UPLOAD ---")
        # print(images)

        return images