from django.core.management.base import BaseCommand
import boto3
from django.conf import settings
import os
import requests
import time
import csv  # Import CSV module
from upload.models import Image
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'List and process all images in the specified S3 bucket and extract the image ID'

    def handle(self, *args, **kwargs):
        # Initialize an S3 client with credentials from Django settings.
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME  # The name of the S3 bucket to connect to.
        self.stdout.write(f"Connecting to S3 bucket: {bucket_name}")
        
        # Ensure an admin user exists, or create one if not.
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'password': 'adminpassword'})
        if created:
            self.stdout.write("Created default admin user.")
        else:
            self.stdout.write("Found existing admin user.")
        
        added_count = 0  # Counter for successfully added images.
        not_found_count = 0  # Counter for images that don't have a corresponding product in the API.
        failed_items = []  # List to track failed part numbers

        continuation_token = None  # Token for paginating through large S3 buckets.
        while True:
            try:
                # List objects in the S3 bucket, using a continuation token if there are multiple pages.
                if continuation_token:
                    response = s3_client.list_objects_v2(Bucket=bucket_name, ContinuationToken=continuation_token)
                else:
                    response = s3_client.list_objects_v2(Bucket=bucket_name)

                # Process each object in the bucket if there are any.
                if 'Contents' in response:
                    for obj in response['Contents']:
                        key = obj['Key']  # The key is the object's path in the bucket.

                        # Skip directories or objects that don't represent files.
                        if key.endswith('/'):
                            continue

                        # Extract the filename and derive the image ID from it.
                        parts = key.split('/')
                        file_name = parts[-1]
                        image_id = os.path.splitext(file_name)[0].strip()

                        # Skip if the filename or image ID is invalid.
                        if not file_name or not image_id or not image_id.isalnum():
                            continue

                        # Helper function to make an API request and return the product list
                        def fetch_product_data(item_code):
                            api_url = 'https://auth.saccloud.co.za/api/rest/searchProducts'
                            headers = {
                                "content-type": 'application/json',
                                'x-hasura-admin-secret': 'S@CC0mmercialP@rts!@#123'
                            }
                            params = {'itemCode': '100' + item_code}
                            try:
                                api_response = requests.post(api_url, headers=headers, json=params)
                                api_response.raise_for_status()  # Raise an error if the API response is not successful.
                                api_data = api_response.json()
                                return api_data.get('repd_productMaster', [])
                            except requests.RequestException as e:
                                self.stdout.write(f"API request failed for image ID {item_code}: {str(e)}")
                                return []

                        try:
                            # Check if an image with the same stock number already exists.
                            Image.objects.get(stockNo=image_id)
                            continue  # Skip processing if the image already exists.
                        except Image.DoesNotExist:
                            # Try fetching product data with the original image ID.
                            product_list = fetch_product_data(image_id)

                            # Retry logic: If no product is found and the image ID ends with certain suffixes.
                            if not product_list and (image_id.endswith(('a', 'b', 'c', '_a', '_b', '_c'))):
                                # Remove the suffix and try again.
                                image_id_cleaned = image_id.rstrip('abc_')  # Removes 'a', 'b', 'c', '_a', '_b', '_c'
                                self.stdout.write(f"Retrying with cleaned image ID: {image_id_cleaned}")
                                product_list = fetch_product_data(image_id_cleaned)

                            if product_list:
                                # Extract and prepare initial data for the Image object.
                                product_data = product_list[0]
                                initial_data = {
                                    'stockNo': product_data['itemCode'][3:],  # Remove the '100' prefix.
                                    'description': product_data['itemDescription'],
                                    'added_by': admin_user  # Assign the admin user as the 'added_by' user.
                                }

                                image = Image(**initial_data)  # Create a new Image object.
                                s3_response = s3_client.get_object(Bucket=bucket_name, Key=key)
                                image_content = s3_response['Body'].read()  # Read the image content from S3.

                                image_file = ContentFile(image_content)  # Create a Django file object.
                                image_file.name = file_name

                                image.url_a1.save(image_file.name, image_file)  # Save the image to the 'url_a1' field.
                                image.save()  # Save the Image object to the database.

                                added_count += 1  # Increment the counter for added images.
                            else:
                                # If no product data is found, log this occurrence.
                                self.stdout.write(f"Part number without a product: {file_name}, Image ID: {image_id}")
                                not_found_count += 1  # Increment the counter for not found parts.
                                failed_items.append(image_id)  # Add failed part number to the list
                else:
                    # No objects were found in the bucket.
                    self.stdout.write("No objects found in the bucket.")
                    break
                
                # Handle pagination if the bucket has more than 1000 objects.
                if 'IsTruncated' in response and response['IsTruncated']:  # More pages are available.
                    continuation_token = response['NextContinuationToken']  # Get the token for the next page.
                else:
                    break  # No more pages, exit the loop.
            except Exception as e:
                # Handle any other exceptions that occur during S3 operations.
                self.stdout.write(f"Error listing S3 objects: {str(e)}")
                break

        # Output the total counts of images added and parts not found.
        self.stdout.write(f"Total images added: {added_count}")
        self.stdout.write(f"Total parts not found: {not_found_count}")

        # Write the failed part numbers to a CSV file
        if failed_items:
            csv_file_path = os.path.join(settings.BASE_DIR, 'failed_items.csv')
            with open(csv_file_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Part Number'])  # Write the header
                for part_number in failed_items:
                    csvwriter.writerow([part_number])  # Write each part number

            self.stdout.write(f"Failed items have been written to: {csv_file_path}")
