from django.db import migrations


def seed_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('users', 'SubscriptionPlan')
    defaults = [
        {'name': 'Basic', 'max_active_listings': 5, 'price_monthly': 0, 'featured_boost': False},
        {'name': 'Pro Agent', 'max_active_listings': 50, 'price_monthly': 49, 'featured_boost': True},
        {'name': 'Agency', 'max_active_listings': 300, 'price_monthly': 199, 'featured_boost': True},
    ]
    for row in defaults:
        SubscriptionPlan.objects.update_or_create(name=row['name'], defaults=row)


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(seed_subscription_plans),
    ]
