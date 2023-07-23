import os
import sys

# Took this idea from https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
# I couldn't figure out how to get a sane import path for the tests without this.
PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH,"nasti"
)
sys.path.append(SOURCE_PATH)