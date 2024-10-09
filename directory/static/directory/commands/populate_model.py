from django.core.management.base import BaseCommand
from upload.models import Image, S3MediaStorage
from django.contrib.auth.models import User
import requests
import time
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Populate the model with data from a text file and images from a bucket'

    def handle(self, *args, **kwargs):
        txt_file = 'upload/DAILY-STOCK-100.TXT'
        path_manager = S3MediaStorage()

        # Ensure a default admin user exists
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'password': 'adminpassword'})
        if created:
            self.stdout.write("Created default admin user.")
        else:
            self.stdout.write("Found existing admin user.")

        status_messages = []

        try:
            with open(txt_file, 'r') as file:
                lines = file.readlines()
                for line in lines[1:]:
                    fields = line.strip().split('\t')
                    if len(fields) < 2:
                        continue

                    part_number = fields[0]
                    description = fields[1]

                    # Remove the first three characters from part_number
                    part_number = part_number[3:]

                    # Check if the image already exists in the database
                    image, created = Image.objects.get_or_create(
                        stockNo=part_number,
                        defaults={
                            'description': description,
                            'added_by': admin_user
                        }
                    )
                    if not created:
                        status_messages.append(f"Image for part {part_number} already exists, skipping.")
                        continue

                    # Form the image URLs for both .jpg and .png
                    image_urls = [
                        f"https://sac-cdn-images.sacapps.co.za/prod-img/{part_number}.jpg",
                        f"https://sac-cdn-images.sacapps.co.za/prod-img/{part_number}.png"
                    ]

                    image_found = False
                    for image_url in image_urls:
                        # Check if the image URL exists
                        try:
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                image_content = response.content
                                image_extension = image_url.split('.')[-1]  # Get file extension

                                # Save the image content to the model's ImageField
                                image_file = ContentFile(image_content)
                                image_file.name = f"{part_number}.{image_extension}"  # Set the name attribute for S3 storage

                                # Save the image file to the url_a1 field
                                image.url_a1.save(image_file.name, image_file)
                                image.save()

                                status_messages.append(f"Processed part {part_number}.")
                                image_found = True
                                break
                            else:
                                status_messages.append(f"Image for part {part_number} not found at {image_url}.")
                        except requests.RequestException as e:
                            status_messages.append(f"Failed to fetch image for part {part_number}: {str(e)}")

                    if not image_found:
                        status_messages.append(f"No valid image found for part {part_number}.")

                    # Respectful rate limiting
                    time.sleep(1)  # Sleep time to avoid hitting the server too frequently

        except FileNotFoundError:
            self.stdout.write("Text file not found.")
            return

        self.stdout.write("\n".join(status_messages))
