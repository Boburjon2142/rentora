from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from PIL import Image, ImageDraw

from apps.properties.models import Property, PropertyImage, PropertyType, QarshiDistrict


class Command(BaseCommand):
    help = "Seed default listings with up to 3 generated images per listing."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=24, help='How many listings to create (default: 24).')
        parser.add_argument('--clear', action='store_true', help='Delete all existing listings before seeding.')
        parser.add_argument('--owner', type=str, default='', help='Username of owner for seeded listings.')
        parser.add_argument('--images-per-property', type=int, default=3, help='Images per listing (1..3).')

    @transaction.atomic
    def handle(self, *args, **options):
        count = max(1, options['count'])
        images_per_property = min(max(1, options['images_per_property']), 3)
        owner = self._resolve_owner(options['owner'])

        if options['clear']:
            deleted, _ = Property.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removed old records: {deleted}'))

        property_types = [x[0] for x in PropertyType.choices]
        districts = [x[0] for x in QarshiDistrict.choices]

        created_properties = 0
        created_images = 0

        for i in range(1, count + 1):
            idx = i - 1
            prop = Property.objects.create(
                owner=owner,
                title=f"Default Rasmli E'lon #{i}",
                description=f"Qarshi shahridagi rasmli default e'lon #{i}.",
                property_type=property_types[idx % len(property_types)],
                city='Qarshi',
                district=districts[idx % len(districts)],
                address=f"{(idx % 7) + 1}-mitti tuman, {20 + idx}-uy",
                price=Decimal(220 + idx * 18),
                bedrooms=(idx % 4) + 1,
                bathrooms=(idx % 3) + 1,
                area_m2=52 + idx * 5,
                is_premium=(i % 6 == 0),
                is_active=True,
            )
            created_properties += 1

            for img_idx in range(1, images_per_property + 1):
                image_file = self._build_demo_house_image(prop.title, img_idx, i)
                PropertyImage.objects.create(
                    property=prop,
                    image=image_file,
                    is_primary=(img_idx == 1),
                )
                created_images += 1

        self.stdout.write(self.style.SUCCESS(f'Created listings: {created_properties}'))
        self.stdout.write(self.style.SUCCESS(f'Created images: {created_images}'))
        self.stdout.write(self.style.SUCCESS(f'Owner: {owner.username}'))

    def _resolve_owner(self, username: str):
        user_model = get_user_model()
        if username:
            user = user_model.objects.filter(username=username).first()
            if user:
                return user
            raise CommandError(f"Owner username not found: {username}")

        return (
            user_model.objects.filter(is_superuser=True).first()
            or user_model.objects.first()
            or user_model.objects.create_user(
                username='demoowner',
                password='DemoPass123!',
                email='demo@rentora.local',
            )
        )

    def _build_demo_house_image(self, title: str, image_index: int, seed: int):
        r = 30 + (seed * 11 + image_index * 17) % 120
        g = 110 + (seed * 7 + image_index * 13) % 90
        b = 135 + (seed * 5 + image_index * 19) % 80

        width, height = 1280, 820
        canvas = Image.new('RGB', (width, height), color=(r, g, b))
        draw = ImageDraw.Draw(canvas)

        # Sky strip
        draw.rectangle([(0, 0), (width, 260)], fill=(165, 210, 235))
        # Ground
        draw.rectangle([(0, 260), (width, height)], fill=(115, 160, 105))

        # House body
        draw.rectangle([(360, 300), (920, 680)], fill=(245, 241, 235), outline=(130, 120, 110), width=4)
        # Roof
        draw.polygon([(320, 320), (640, 150), (960, 320)], fill=(180, 65, 60), outline=(120, 40, 35))
        # Door
        draw.rectangle([(600, 500), (700, 680)], fill=(125, 85, 55), outline=(90, 55, 35), width=3)
        # Windows
        draw.rectangle([(430, 420), (550, 520)], fill=(170, 220, 245), outline=(95, 120, 130), width=3)
        draw.rectangle([(740, 420), (860, 520)], fill=(170, 220, 245), outline=(95, 120, 130), width=3)

        draw.text((48, 48), title, fill=(255, 255, 255))
        draw.text((48, 92), f'Rasm {image_index}', fill=(245, 245, 245))

        buffer = BytesIO()
        canvas.save(buffer, format='JPEG', quality=88)
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f'default_house_{seed}_{image_index}.jpg')
