# Use Fedora as the base image
FROM fedora:latest

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PIPENV_NO_INHERIT=true
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Set working directory in the container
WORKDIR /app

# Install dependencies and pyenv
RUN dnf -y install git gcc make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel findutils && \
    curl https://pyenv.run | bash && \
    pyenv install 3.11.4 && \
    pyenv global 3.11.4

# Confirm Python version
RUN python --version

# Install Pipenv using pip
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the app source code into the container
COPY . .

# Set the entrypoint to our CLI app using pipenv's run command
ENTRYPOINT ["pipenv", "run", "python", "nasti.py"]
