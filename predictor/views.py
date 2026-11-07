from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
from .ml_model import predict_demand
from .models import PredictionHistory, MeterReading, Notification

HIGH_DEMAND_THRESHOLD = 8.0
MODERATE_DEMAND_THRESHOLD = 4.0


def create_usage_notification(user, demand):
    """Create an in-app alert for a demand value and return its status."""
    demand = float(demand)

    if demand >= HIGH_DEMAND_THRESHOLD:
        status = "High"
        message = (
            f"High electricity demand detected: {demand:.2f} kW. "
            "Reduce high-power appliance usage and check your consumption."
        )
    elif demand >= MODERATE_DEMAND_THRESHOLD:
        status = "Moderate"
        message = (
            f"Moderate electricity demand detected: {demand:.2f} kW. "
            "Monitor your usage and avoid running multiple high-power appliances together."
        )
    else:
        return None

    Notification.objects.create(user=user, message=message, status=status)
    return status, message


def send_usage_email(user, status, message):
    """Send an optional email without breaking the app if SMTP is unavailable."""
    if not user.email:
        return
    try:
        send_mail(
            f"{status} Electricity Usage Alert",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
    except Exception:
        # In-app notifications are the primary alert channel.
        pass


@login_required(login_url='login')
def home(request):

    prediction = None

    if request.method == "POST":

        data = [
            float(request.POST["global_reactive_power"]),
            float(request.POST["voltage"]),
            float(request.POST["global_intensity"]),
            float(request.POST["sub_metering_1"]),
            float(request.POST["sub_metering_2"]),
            float(request.POST["sub_metering_3"]),
            int(request.POST["hour"]),
            int(request.POST["day"]),
            int(request.POST["month"]),
            int(request.POST["year"])
        ]

        prediction = predict_demand(data)

        PredictionHistory.objects.create(
            user=request.user,
            global_reactive_power=data[0],
            voltage=data[1],
            global_intensity=data[2],
            sub_metering_1=data[3],
            sub_metering_2=data[4],
            sub_metering_3=data[5],
            hour=data[6],
            day=data[7],
            month=data[8],
            year=data[9],
            prediction=prediction
        )

        notification = create_usage_notification(request.user, prediction)
        if notification:
            status, message = notification
            send_usage_email(request.user, status, message)
            if status == "High":
                messages.error(request, message)
            else:
                messages.warning(request, message)
        else:
            messages.success(request, "Prediction saved successfully.")

    return render(request, "index.html", {
        "prediction": prediction
    })
@login_required(login_url='login')
def meter_reading(request):

    if request.method == "POST":

        reading = float(request.POST["reading"])

        reading_date = datetime.strptime(
            request.POST["reading_date"],
            "%Y-%m-%d"
        ).date()

        # Save current reading
        current_reading = MeterReading.objects.create(
            user=request.user,
            reading=reading,
            reading_date=reading_date
        )

        # Get previous reading
        previous_reading = MeterReading.objects.filter(
            user=request.user
        ).exclude(
            id=current_reading.id
        ).order_by(
            "-reading_date",
            "-created_at"
        ).first()

        # Continue only if previous reading exists
        if previous_reading:

            # Calculate consumed units
            units_consumed = (
                reading - previous_reading.reading
            )

            # Calculate number of days
            days = (
                current_reading.reading_date -
                previous_reading.reading_date
            ).days

            if days <= 0:
                days = 1

            # Daily electricity usage
            daily_usage = units_consumed / days

            # Get older readings
            older_readings = MeterReading.objects.filter(
                user=request.user
            ).exclude(
                id=current_reading.id
            ).order_by(
                "-reading_date",
                "-created_at"
            )

            # Calculate historical daily usage
            historical_daily_usage = []

            readings_list = list(older_readings)

            for i in range(len(readings_list) - 1):

                newer = readings_list[i]
                older = readings_list[i + 1]

                old_units = (
                    newer.reading -
                    older.reading
                )

                old_days = (
                    newer.reading_date -
                    older.reading_date
                ).days

                if old_days <= 0:
                    old_days = 1

                old_daily_usage = (
                    old_units / old_days
                )

                if old_daily_usage >= 0:
                    historical_daily_usage.append(
                        old_daily_usage
                    )

            # Check if historical usage is available
            if historical_daily_usage:

                average_daily_usage = (
                    sum(historical_daily_usage) /
                    len(historical_daily_usage)
                )

                # HIGH USAGE
                if daily_usage > average_daily_usage * 1.20:

                    message = (
                        f"Your daily electricity usage is "
                        f"{daily_usage:.2f} kWh/day, which is "
                        f"significantly higher than your usual "
                        f"average of {average_daily_usage:.2f} "
                        f"kWh/day."
                    )

                    Notification.objects.create(
                        user=request.user,
                        message=message,
                        status="High"
                    )

                    # Send email
                    if request.user.email:

                        send_usage_email(request.user, "High", message)

                # MODERATE USAGE
                elif daily_usage > average_daily_usage * 1.10:

                    message = (
                        f"Your daily electricity usage is "
                        f"{daily_usage:.2f} kWh/day, which is "
                        f"slightly higher than your usual "
                        f"average of {average_daily_usage:.2f} "
                        f"kWh/day."
                    )

                    Notification.objects.create(
                        user=request.user,
                        message=message,
                        status="Moderate"
                    )

                    # Send email
                    if request.user.email:

                        send_usage_email(request.user, "Moderate", message)

    # Show latest reading
    latest_reading = MeterReading.objects.filter(
        user=request.user
    ).order_by(
        "-reading_date",
        "-created_at"
    ).first()

    return render(
        request,
        "meter_reading.html",
        {
            "latest_reading": latest_reading
        }
    )
@login_required(login_url='login')
def dashboard(request):

    records = PredictionHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')

    total_predictions = records.count()

    average_prediction = records.aggregate(
        Avg('prediction')
    )['prediction__avg']

    highest_prediction = records.aggregate(
        Max('prediction')
    )['prediction__max']

    latest_prediction = records.first()

    # Last 7 predictions
    recent_predictions = list(records[:7])
    recent_predictions.reverse()

    # Date + Time labels
    chart_labels = [
        item.created_at.strftime('%d-%m %I:%M %p')
        for item in recent_predictions
    ]

    chart_data = [
        float(item.prediction)
        for item in recent_predictions
    ]

    context = {
        'total_predictions': total_predictions,
        'average_prediction': average_prediction,
        'highest_prediction': highest_prediction,
        'latest_prediction': latest_prediction,

        'recent_predictions': recent_predictions,

        'chart_labels': chart_labels,
        'chart_data': chart_data,

        'bar_labels': chart_labels,
        'bar_data': chart_data,
    }

    return render(
        request,
        'dashboard.html',
        context
    )
@login_required(login_url='login')
def history(request):
    predictions = PredictionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "history.html",
        {
            "predictions": predictions,
            "records": predictions,
        }
    )
@login_required(login_url='login')
def notifications(request):

    alerts = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "notifications.html",
        {
            "alerts": alerts
        }
    )
