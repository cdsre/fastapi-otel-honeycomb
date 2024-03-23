from fastapi import FastAPI
from random import randint
from time import sleep
from opentelemetry import trace

tracer = trace.get_tracer("cdsre.tracer.fastapi.app")
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {format_name(name)}"}


@app.get("/sleep")
async def my_sleep():
    sleep_time = random_sleep()
    return {"message": f"slept for {sleep_time}"}


@app.get("/slow_hello/{name}")
async def slow_hello(name: str):
    formatted_name = format_name(name, slow=True)
    return {"message": f"Hello {formatted_name}"}


@app.get("/exception")
async def exception():
    span = trace.get_current_span()
    span.add_event("pre_exception_event", attributes={"stage": "pre_exception"})
    sleep(0.1)
    try:
        span.add_event("try_exception_event", attributes={"stage": "during_exception", "foo": ["bar", "baz"]})
        sleep(0.1)
        raise ValueError("Something went wrong")
    except ValueError as ve:
        span.add_event("catch_exception_event", attributes={"stage": "caught_exception"})
        sleep(0.1)
        span.record_exception(ve)
        span.set_status(trace.StatusCode(2))
        return {"error": str(ve)}


@tracer.start_as_current_span("random_sleep")
def random_sleep() -> int:
    sleep_time = randint(1, 5)

    span = trace.get_current_span()
    span.set_attribute("sleep_time", sleep_time)

    sleep(sleep_time)
    return sleep_time


@tracer.start_as_current_span("format_name")
def format_name(name: str, slow: bool = False) -> str:
    span = trace.get_current_span()
    span.set_attribute("slow", slow)
    if slow:
        random_sleep()
        random_sleep()
    return name.title()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
