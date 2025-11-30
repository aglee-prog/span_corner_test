from datetime import datetime
from classes import BehaviorTestFactory
from utils.common_utils import get_files_or_fail
#### BEHAVIOR TESTS REGISTRY
from behaviour_tests import CornerExtBehaviorTest

import warnings
import click
import os

warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


@click.group()
def main():
    pass


test_type = "Corner"


@click.command(context_settings={'show_default': True})
@click.option("--path", prompt="Path to video", type=click.Path(exists=True, file_okay=True))
@click.option('--model', type=click.Choice(['rats', 'mice']), default="mice", prompt="Select model")
def watch(path, model):
    click.secho('Watch video ', fg='blue')
    behavior_test = BehaviorTestFactory.create(test_type)
    behavior_test.watch(model, path)
    click.secho('Done ', fg='blue')


@click.command(context_settings={'show_default': True})
@click.option("--path", prompt="Path to video", type=click.Path(exists=True, file_okay=True))
@click.option('--model', type=click.Choice(['rats', 'mice']), default="mice", prompt="Select model")
def create(path, model):
    csv_path = os.path.join(path, 'report_' + datetime.now().strftime("%b_%d_%Y_%H_%M") + '.csv')
    files = get_files_or_fail(path)
    click.secho('Create videos', fg='blue')
    behavior_test = BehaviorTestFactory.create(test_type)
    click.secho('Create video ', fg='blue')
    click.secho('Model: ' + model, fg='blue')
    click.secho('Path: ' + path, fg='blue')
    for video_file in files:
        output_file = video_file.replace('.mp4', '-output.mp4')
        if os.path.isfile(output_file):
            click.secho('Skip file path: ' + path + '. File exists.', fg='blue')
        else:
            behavior_test.create(model, video_file, csv_path)

    click.secho('Done ', fg='blue')


main.add_command(watch)
main.add_command(create)

if __name__ == "__main__":
    main()
