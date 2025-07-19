from django.core.management.base import BaseCommand
from apps.roles.models import Permission

class Command(BaseCommand):
    help = 'Initialize default permissions for all features'

    def handle(self, *args, **kwargs):
        # Define all default permissions
        default_permissions = {
            'integrations': [
                ('view', 'Can view integrations'),
                ('edit', 'Can edit integrations'),
                ('toggle', 'Can toggle integrations status'),
            ],
            'config': [
                ('view', 'Can view configuration'),
                ('edit', 'Can edit configuration'),
                ('toggle', 'Can toggle configuration differents status'),
            ],
            'roles': [
                ('view', 'Can view roles'),
                ('create', 'Can create roles'),
                ('edit', 'Can edit roles'),
                ('delete', 'Can delete roles'),
                ('toggle', 'Can toggle roles status'),
            ],
            'mail_settings': [
                ('view', 'Can view mail settings'),
                ('edit', 'Can edit mail settings'),
                ('toggle', 'Can toggle mail settings status'),
            ],
            'alerts': [
                ('view', 'Can view alerts'),
                ('manage', 'Can manage alerts status'),
                ('send_email', 'Can send alert emails'),
            ],
            'defacement': [
                ('view', 'Can view defacement data'),
                ('reset', 'Can reset defacement values'),
            ],
            'vendor_list': [
                ('view', 'Can view vendor list'),
                ('create', 'Can add vendors'),
                ('edit', 'Can edit vendors'),
                ('delete', 'Can delete vendors'),
            ],
            'logs': [
                ('view', 'Can view logs'),
                ('export', 'Can export logs'),
            ],
            'focal_functions': [
                ('view', 'Can view focal functions'),
                ('create', 'Can create focal functions'),
                ('edit', 'Can edit focal functions'),
                ('delete', 'Can delete focal functions'),
            ],
            'focal_points': [
                ('view', 'Can view focal points'),
                ('create', 'Can create focal points'),
                ('edit', 'Can edit focal points'),
                ('delete', 'Can delete focal points'),
                ('toggle', 'Can toggle focal points status'),
            ],
            'entities': [
                ('view', 'Can view entities'),
                ('create', 'Can create entities'),
                ('edit', 'Can edit entities'),
                ('delete', 'Can delete entities'),
            ],
            'platforms': [
                ('view', 'Can view platforms'),
                ('create', 'Can create platforms'),
                ('edit', 'Can edit platforms'),
                ('delete', 'Can delete platforms'),
                ('toggle', 'Can toggle platforms status'),
            ],
            'users': [
                ('view', 'Can view users'),
                ('create', 'Can create users'),
                ('edit', 'Can edit users'),
                ('delete', 'Can delete users'),
                ('manage_roles', 'Can manage user roles'),
                ('toggle', 'Can toggle users status'),
            ],
            'dashboard': [
                ('view', 'Can view the dashboard'),
                ('carousel_view', 'can view carousel'),
            ],
            'cerb_scans': [
                ('view', 'Can view detail about subscan'),
                ('manage', 'Can manage subscan config'),
                ('toggle', 'Can toggle subscan status'),
            ]
        }

        # Create permissions
        for feature, permissions in default_permissions.items():
            for permission_name, description in permissions:
                permission_code = f"{feature}_{permission_name}"
                Permission.objects.get_or_create(
                    feature_name=feature,
                    permission_name=permission_name,
                    permission_code=permission_code,
                    defaults={'description': description}
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission: {permission_code}')
                )


        try:
            # Create the Super Admin role if it doesn't exist
            from apps.roles.models import Role, RolePermission
            super_admin_role, created = Role.objects.get_or_create(
                name='Super Admin',
                defaults={'description': 'Role with all permissions'}
            )

            # Assigne all permissions to the Super Admin role
            all_permissions = Permission.objects.all()
            for permission in all_permissions:
                RolePermission.objects.get_or_create(
                    role=super_admin_role,
                    permission=permission
                )

            if created:
                self.stdout.write(
                    self.style.SUCCESS('Created Super Admin role with all permissions')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating Super Admin role: {str(e)}')
            )