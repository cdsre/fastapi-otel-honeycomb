# OTEl Example with FastAPI

This repo is an annotated fastapi example that uses honeycomb as the destination for OTEL traffic. It is using honeycombs
own [distro](https://pypi.org/project/honeycomb-opentelemetry/) for easy integration of OTEL. However also uses OTEL
package to add attributes to spans or start new spans.

In this example we are using [honeycomb](https://www.honeycomb.io/) as the backend for the telemetry data. Honeycomb 
provides a free tier allowing you to ingest 20million events per month.

The [get-started doc](https://docs.honeycomb.io/get-started/start-building/application/) has good working examples that
were used to build this setup.

# Setup

## pip
Install the honeycomb-opentelemetry distro in a virtual env with the below command. Note that the `--pre` flag is 
important because the package is still in `beta`.

```shell
python -m pip install honeycomb-opentelemetry fastapi uvicorn --pre
```

Alternativly you can set up the environment from the requirements file. If you do this you can skip the auto instrument
section below.

```shell
pip install -r requirements.txt
```

## Auto Instrument
OTEL provides several packages that will auto instrument our code. In this example it will generate events/spans with 
trace ids for the inbound and outbound requests to our app. This is a good starting point so we need to pull in these 
instrumentation packages. the below command will pull in all auto-instrumentation packages. For the purpose of this demo
this is fine.

```shell
opentelemetry-bootstrap --action=install
```

## Environment
In order to be able to ship our data to the honeycomb backend we need to set the following environment variables. You 
can create an API key from your honeycomb account, and the service name is what ever you want this to show under in the
backend.

```shell
export HONEYCOMB_API_KEY=neqfoeXXXXXXXOac0mwYf
export OTEL_SERVICE_NAME=my-service-name
```

# Running
In order to run this we use a command opentelemetry packages installed for us. We pass the command to run under 
instrumentation

```shell
opentelemetry-instrument python main.py

INFO:     Started server process [21264]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

# Traces

## Auto instrumented trace
We can look at a single trace for a request to the `/hello/{name}` route. This trace was in the early stages of this repo
when we were only using auto-instrumentation

```shell
curl http://localhost:8000/hello/chris
{"message":"Hello Chris"}
```

![hello-name-only-auto](./images/hello-name-only-auto.png)

So what does this trace tell us? Well is shows us the event spans as a waterfall chart. We will see more of this later.
It also shows us `fields` which in OTEL language are `attributes` about the event. These are shown on the right-hand side
in honeycomb. We can filter the fields in this trace like showing just fields related to http. Some interesting points 
here are we can see not just the `http.target` (after interpolation), but we can also see the `http.route` which is the 
template path in our app.

![hello-name-http-fields](./images/hello-name-http-fields.png)

## Creating spans - methods
Using the OTEL library we can use a decorator in python to create a new span when a function or method is called.

```python
@tracer.start_as_current_span("random_sleep")
def random_sleep() -> int:
    sleep_time = randint(1, 5)
    sleep(sleep_time)
    return sleep_time
```

Now when we call the `/sleep` route in our app which in turn calls our random_sleep function it gets its own trace

![sleep-trace](./images/sleep-trace.png)

We can instrument other functions like this. As an example we introduced a slow_name route which will call the format
name function passing the slow flag as `True`. This will then call the random_sleep function twice. Since that route is
auto-instrumented, and we have decorated our sleep and format functions we now get a span for each function call.

![slow-name-trace](./images/slow-name-trace.png)

## Adding Attributes to Spans
We can get access to the current span and allow us to add our own custom attributes to the span. This model is popular
in observability 2.0 movement where wide events are the norm. Anything of interest that happens in your unit of work 
should be added to the span. 

For example, we can instrument the sleep function to add the sleep time into the span.

```python
    sleep_time = randint(1, 5)

    span = trace.get_current_span()
    span.set_attribute("sleep_time", sleep_time)
```

![sleep-time-attribute](./images/sleep-time-attribute.png)

In this case it's not incredibly useful, but it shows the value of setting variables in the span for easy debugging or
slicing and dicing data. However, we can then search our events for all traces where the sleep time was less than 3 for 
example

![sleep-time-less-than-3](./images/sleep-time-attribute-less-than-3.png)

This then becomes very powerful to allow us to ask questions about our data.
