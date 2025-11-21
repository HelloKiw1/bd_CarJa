from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps


class Command(BaseCommand):
    help = 'Create default groups for the project: locatario and administrador, and assign model permissions.'

    def handle(self, *args, **options):
        # Define groups and desired permissions per app/model
        roles = {
            'administrador': {
                # full CRUD on veiculo and anuncio
                'veiculo': ['add', 'change', 'delete', 'view'],
                'anuncio': ['add', 'change', 'delete', 'view'],
            },
            'locatario': {
                # read access to veiculo and anuncio and ability to add anuncio (if applicable)
                'veiculo': ['view'],
                'anuncio': ['view', 'add'],
            }
        }

        for group_name, models in roles.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group '{group_name}'"))
            else:
                self.stdout.write(self.style.NOTICE(f"Group '{group_name}' already exists"))

            # collect permissions
            perms_to_add = []
            for app_label_model, actions in models.items():
                app_label = app_label_model
                # model name is title-cased in this mapping
                model_name = app_label_model.capitalize()
                try:
                    model = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stdout.write(self.style.WARNING(
                        f"Model {model_name} in app '{app_label}' not found; skipping."))
                    continue

                for action in actions:
                    codename = f"{action}_{model._meta.model_name}"
                    try:
                        perm = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Permission '{codename}' for app '{app_label}' not found; skipping."))
                        continue
                    perms_to_add.append(perm)

            if perms_to_add:
                group.permissions.set(list({p.pk: p for p in perms_to_add}.values()))
                self.stdout.write(self.style.SUCCESS(f"Assigned permissions to group '{group_name}'"))
            else:
                self.stdout.write(self.style.WARNING(f"No permissions assigned to group '{group_name}'"))

        self.stdout.write(self.style.SUCCESS('Role creation finished.'))
