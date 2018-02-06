# getStatus

This is a sample Python application, using the Flask microframework, for use with Wercker.  This application uses the `2.7:slim` container obtained from the [Docker Hub](https://hub.docker.com/_/python/)

The application queries Bitbucket, GitLab and Git Hub to verify they are up and running.

## Setup and Build
Firstly, ensure you have the [wercker cli installed](http://devcenter.wercker.com/docs/cli/installation).

Now clone this repo and cd into the directory:

```
git clone https://github.com/wercker/getting-started-python.git
cd getting-started-python
```

To build and test the app:
```
wercker build
```

## Running
You can run the sample app in a couple of different ways. With Flask installed locally along with Python, the first is to simply launch the sample app:
```
python app.py
```

Now point your browser at `http://localhost:5000` to see:
```
Hello World!
```
or at `http://localhost:5000/status

The second, and more useful, way is to use the `wercker dev` command to launch the binary within a Docker container, using the base image defined in the `box:id` property at the top of the `wercker.yml`, like so:
```
wercker dev --expose-ports
```
The `dev` target inside `wercker.yml` uses the `internal/watch` step to dynamically reload the runtime container when sourcefile changes are detected, which allows you to quickly test changes without having to kill/rebuild/relaunch the container.

