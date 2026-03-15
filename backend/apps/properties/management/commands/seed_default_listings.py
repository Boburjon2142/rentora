from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from PIL import Image, ImageDraw

from apps.properties.models import Property, PropertyImage, PropertyType, QarshiDistrict


class Command(BaseCommand):
    help = "Seed default listings with up to 3 generated images per listing."
    DEFAULT_IMAGE_SOURCE_DIR = Path(r"C:\Users\Omen\Desktop\rentoraxon")

    PRICE_VARIANTS = {
        1: (168, 182, 197),
        2: (220, 245, 285),
        3: (315, 348, 392),
        4: (438, 472, 525),
    }

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=24, help='How many listings to create (default: 24).')
        parser.add_argument('--clear', action='store_true', help='Delete all existing listings before seeding.')
        parser.add_argument('--owner', type=str, default='', help='Username of owner for seeded listings.')
        parser.add_argument('--images-per-property', type=int, default=3, help='Images per listing (1..3).')
        parser.add_argument('--image-source-dir', type=str, default='', help='Optional directory with source listing images.')

    @transaction.atomic
    def handle(self, *args, **options):
        count = max(1, options['count'])
        images_per_property = min(max(1, options['images_per_property']), 3)
        owner = self._resolve_owner(options['owner'])
        source_images = self._get_source_images(options['image_source_dir'])

        if options['clear']:
            deleted, _ = Property.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removed old records: {deleted}'))

        property_types = [x[0] for x in PropertyType.choices]
        districts = [x[0] for x in QarshiDistrict.choices]

        created_properties = 0
        created_images = 0

        for i in range(1, count + 1):
            idx = i - 1
            bedrooms = (idx % 4) + 1
            prop = Property.objects.create(
                owner=owner,
                title=f"Default Rasmli E'lon #{i}",
                description=f"Qarshi shahridagi {bedrooms} xonali qulay xonadon #{i}.",
                property_type=property_types[idx % len(property_types)],
                city='Qarshi',
                district=districts[idx % len(districts)],
                address=f"{(idx % 7) + 1}-mitti tuman, {20 + idx}-uy",
                price=self._build_price(bedrooms, idx),
                bedrooms=bedrooms,
                bathrooms=(idx % 3) + 1,
                area_m2=52 + idx * 5,
                is_premium=(i % 6 == 0),
                is_active=True,
            )
            created_properties += 1

            for img_idx in range(1, images_per_property + 1):
                image_file = self._build_image_file(prop.title, img_idx, i, source_images)
                PropertyImage.objects.create(
                    property=prop,
                    image=image_file,
                    is_primary=(img_idx == 1),
                )
                created_images += 1

        self.stdout.write(self.style.SUCCESS(f'Created listings: {created_properties}'))
        self.stdout.write(self.style.SUCCESS(f'Created images: {created_images}'))
        self.stdout.write(self.style.SUCCESS(f'Owner: {owner.username}'))
        if source_images:
            self.stdout.write(self.style.SUCCESS(f'Image source: {source_images[0].parent}'))
        else:
            self.stdout.write(self.style.WARNING('Image source topilmadi, demo-generated rasmlar ishlatildi.'))

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

    def _build_price(self, bedrooms: int, idx: int) -> Decimal:
        variants = self.PRICE_VARIANTS.get(bedrooms, self.PRICE_VARIANTS[4])
        return Decimal(str(variants[idx % len(variants)]))

    def _get_source_images(self, source_dir_option: str):
        source_dir = Path(source_dir_option) if source_dir_option else self.DEFAULT_IMAGE_SOURCE_DIR
        if not source_dir.exists() or not source_dir.is_dir():
            return []

        return sorted(
            path for path in source_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
        )

    def _build_image_file(self, title: str, image_index: int, seed: int, source_images):
        if source_images:
            image_path = source_images[((seed - 1) * 3 + (image_index - 1)) % len(source_images)]
            with image_path.open('rb') as image_handle:
                return ContentFile(image_handle.read(), name=image_path.name)

        return self._build_demo_house_image(title, image_index, seed)

    def _build_demo_house_image(self, title: str, image_index: int, seed: int):
        width, height = 1280, 820
        canvas = Image.new('RGB', (width, height), color=(235, 239, 244))
        draw = ImageDraw.Draw(canvas)

        sky_top = (125 + (seed * 7) % 35, 184 + (image_index * 9) % 25, 228)
        sky_bottom = (224, 236, 244)
        for y in range(0, 360):
            ratio = y / 359
            color = tuple(
                int(sky_top[channel] * (1 - ratio) + sky_bottom[channel] * ratio)
                for channel in range(3)
            )
            draw.line([(0, y), (width, y)], fill=color)

        ground_color = (
            124 + (seed * 5) % 35,
            156 + (image_index * 11) % 45,
            108 + (seed * 3) % 30,
        )
        draw.rectangle([(0, 360), (width, height)], fill=ground_color)
        draw.ellipse([(1040, 54), (1140, 154)], fill=(248, 214, 120))

        house_palette = [
            ((244, 238, 230), (182, 93, 74), (124, 92, 70)),
            ((236, 232, 222), (120, 88, 112), (96, 78, 63)),
            ((230, 238, 233), (90, 118, 98), (98, 82, 68)),
        ]
        wall_color, roof_color, accent_color = house_palette[(seed + image_index) % len(house_palette)]

        left = 250 + image_index * 45
        top = 290 + (seed % 3) * 8
        right = 950 - image_index * 28
        bottom = 690
        roof_peak_x = (left + right) // 2
        roof_peak_y = 150 + image_index * 14

        draw.rounded_rectangle([(left, top), (right, bottom)], radius=14, fill=wall_color, outline=(126, 119, 112), width=4)
        draw.polygon(
            [(left - 30, top + 18), (roof_peak_x, roof_peak_y), (right + 30, top + 18)],
            fill=roof_color,
            outline=(90, 62, 52),
        )
        draw.polygon(
            [(left - 30, top + 18), (roof_peak_x, roof_peak_y), (right + 30, top + 18)],
            outline=(90, 62, 52),
        )

        path_left = roof_peak_x - 90
        path_right = roof_peak_x + 85
        draw.polygon(
            [(path_left, bottom), (path_right, bottom), (path_right + 65, height), (path_left - 55, height)],
            fill=(206, 194, 176),
        )

        door_left = roof_peak_x - 58
        door_right = roof_peak_x + 42
        door_top = 485
        draw.rounded_rectangle([(door_left, door_top), (door_right, bottom)], radius=10, fill=accent_color, outline=(82, 62, 49), width=3)

        window_top = 410
        window_bottom = 525
        for win_left in (left + 85, right - 200):
            win_right = win_left + 120
            draw.rounded_rectangle([(win_left, window_top), (win_right, window_bottom)], radius=8, fill=(170, 215, 238), outline=(92, 123, 132), width=3)
            draw.line([(win_left + 60, window_top), (win_left + 60, window_bottom)], fill=(92, 123, 132), width=3)
            draw.line([(win_left, window_top + 58), (win_right, window_top + 58)], fill=(92, 123, 132), width=3)

        if image_index != 2:
            garage_left = right + 20
            garage_right = min(width - 90, garage_left + 180)
            draw.rounded_rectangle([(garage_left, 395), (garage_right, bottom)], radius=10, fill=(228, 224, 216), outline=(124, 118, 112), width=3)
            draw.rectangle([(garage_left + 22, 470), (garage_right - 22, bottom)], fill=(214, 213, 208), outline=(148, 148, 148), width=2)

        for tree_x in (160 + image_index * 40, 1080 - image_index * 55):
            draw.rectangle([(tree_x, 430), (tree_x + 20, 610)], fill=(112, 79, 58))
            draw.ellipse([(tree_x - 55, 360), (tree_x + 75, 500)], fill=(76, 129, 78))
            draw.ellipse([(tree_x - 30, 322), (tree_x + 100, 460)], fill=(92, 151, 94))

        fence_y = 640
        for fence_x in range(80, width - 40, 42):
            draw.rectangle([(fence_x, fence_y), (fence_x + 10, fence_y + 72)], fill=(238, 232, 220))
        draw.rectangle([(60, fence_y + 18), (width - 60, fence_y + 26)], fill=(232, 226, 213))
        draw.rectangle([(60, fence_y + 58), (width - 60, fence_y + 66)], fill=(232, 226, 213))

        draw.text((42, 36), "Rentora", fill=(255, 255, 255))
        draw.text((42, 78), f"Qarshi demo listing #{seed} | rasm {image_index}", fill=(248, 250, 252))

        buffer = BytesIO()
        canvas.save(buffer, format='JPEG', quality=88)
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f'default_house_{seed}_{image_index}.jpg')
