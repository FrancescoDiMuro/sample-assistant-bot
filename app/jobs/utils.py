from re import Pattern, compile
from telegram.ext import ContextTypes


async def get_jobs_by_name_custom(context: ContextTypes.DEFAULT_TYPE, name: str | Pattern) -> tuple:

    jobs = context.job_queue.jobs()

    pattern = compile(pattern=name)

    return tuple(job for job in jobs if pattern.search(string=job.name))

