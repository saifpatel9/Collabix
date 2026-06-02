# Generated migration for OrganizationPosition model updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_designation_employeehierarchy_organizationposition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationposition',
            name='reporting_position',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='child_positions',
                to='employees.organizationposition'
            ),
        ),
        migrations.AddConstraint(
            model_name='organizationposition',
            constraint=models.UniqueConstraint(
                fields=['employee'],
                name='unique_employee_position'
            ),
        ),
    ]
