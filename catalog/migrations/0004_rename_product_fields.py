from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_flowerkind_product_flower_kinds"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="type",
            new_name="festival",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="flower_kinds",
            new_name="type",
        ),
    ]
