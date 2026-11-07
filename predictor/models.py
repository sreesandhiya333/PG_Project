from django.db import models
from django.contrib.auth.models import User


class PredictionHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    global_reactive_power = models.FloatField()

    voltage = models.FloatField()

    global_intensity = models.FloatField()

    sub_metering_1 = models.FloatField()

    sub_metering_2 = models.FloatField()

    sub_metering_3 = models.FloatField()

    hour = models.IntegerField()

    day = models.IntegerField()

    month = models.IntegerField()

    year = models.IntegerField()

    prediction = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.prediction} kW"


class MeterReading(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    reading = models.FloatField()

    reading_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.reading}"


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.status} - {self.user.username}"