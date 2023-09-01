from django.apps import apps
from django.core.management.base import BaseCommand
from insitu.models import User


class Command(BaseCommand):
    help = (
        "Use in case the relation state gets out of sync from the requirement state."
    )

    def add_arguments(self, parser):
        parser.add_argument("object_type", type=str)
        parser.add_argument("id", type=int)
        parser.add_argument("old_username", type=str)
        parser.add_argument("new_username", type=str)

    def transfer_ownership_on_object(self, obj, **options):
        new_user = User.objects.get(username=options["new_username"])
        old_user = obj.created_by
        obj.created_by = new_user
        obj.set_owner_history(old_user)
        obj.save()

    def handle(self, *args, **options):
        model = apps.get_model("insitu", options["object_type"])

        obj = model.objects.filter(id=options["id"]).first()
        if not obj:
            print(
                "{} object with id {} was not found.".format(
                    options["object_type"], options["id"]
                )
            )
            return

        if obj.created_by.username != options["old_username"]:
            print(
                "{} {} is not created by {}".format(
                    options["object_type"], options["id"], options["old_username"]
                )
            )
            return
        print(
            "Transfering ownership on {} {} from {} to {}".format(
                options["object_type"],
                options["id"],
                options["old_username"],
                options["new_username"],
            )
        )
        related_objects = obj.get_related_objects()
        self.transfer_ownership_on_object(obj, **options)
        for related_object in related_objects:
            self.transfer_ownership_on_object(related_object, **options)
