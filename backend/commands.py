import click
from flask.cli import with_appcontext

@click.command()
@with_appcontext
def run_daily_tasks():
    """Run daily aggregation tasks"""
    try:
        from backend.tasks.scheduled_tasks import run_daily_tasks as daily_tasks
        daily_tasks()
        click.echo("Daily tasks completed!")
    except Exception as e:
        click.echo(f"Error running daily tasks: {str(e)}", err=True)

@click.command()
@with_appcontext
def generate_lms_summary():
    """Generate LMS daily summary for yesterday"""
    try:
        from backend.services.lms_summary_service import LMSSummaryService
        LMSSummaryService.generate_daily_summary()
        click.echo("LMS summary generated!")
    except Exception as e:
        click.echo(f"Error generating LMS summary: {str(e)}", err=True)

@click.command()
@with_appcontext
def update_feature_cache():
    """Update feature cache for all students"""
    try:
        from backend.services.prediction_service import PredictionService
        PredictionService.update_feature_cache_for_all_students()
        click.echo("Feature cache updated!")
    except Exception as e:
        click.echo(f"Error updating feature cache: {str(e)}", err=True)

def register_commands(app):
    """Register all custom commands"""
    app.cli.add_command(run_daily_tasks)
    app.cli.add_command(generate_lms_summary)
    app.cli.add_command(update_feature_cache)