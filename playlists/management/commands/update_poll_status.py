from django.core.management.base import BaseCommand
from django.utils import timezone
from playlists.models import Poll

class Command(BaseCommand):
    help = 'Updates the status of all polls based on their start and end times'

    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0
        
        # Update polls that should be active
        polls_to_activate = Poll.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=False
        )
        for poll in polls_to_activate:
            poll.is_active = True
            poll.save()
            updated_count += 1
        
        # Update polls that should be inactive
        polls_to_deactivate = Poll.objects.filter(
            is_active=True
        ).exclude(
            start_time__lte=now,
            end_time__gte=now
        )
        for poll in polls_to_deactivate:
            poll.is_active = False
            poll.save()
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} polls'))