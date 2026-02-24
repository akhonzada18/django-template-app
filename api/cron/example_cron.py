"""
Example cron job.

To activate a cron job:
1. Implement your logic in the do() method.
2. Register it in core/settings.py under CRON_CLASSES, e.g.:
   CRON_CLASSES = [
       "api.cron.example_cron.ExampleCronJob",
   ]
3. Run manually: python manage.py runcrons
4. In production, schedule: python manage.py runcrons  every minute via cron/systemd.
"""
from django_cron import CronJobBase, Schedule


class ExampleCronJob(CronJobBase):
    # Run every 60 minutes — adjust as needed
    RUN_EVERY_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "api.cron.example_cron.ExampleCronJob"

    def do(self):
        """
        TODO: Implement your cron logic here.
        Example: sync external data, send emails, clean up stale records.
        """
        print("ExampleCronJob running...")
        # e.g. MyModel.objects.filter(expires_at__lt=timezone.now()).delete()
