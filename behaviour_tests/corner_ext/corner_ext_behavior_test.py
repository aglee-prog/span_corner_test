import os

from classes.behavior_test import BehaviorTest
from classes.behavior_test_factory import BehaviorTestFactory
from classes.data_extractors import DLCLiveDataExtractor
from classes.process import Process
from behaviour_tests.common import DataProcessor, ProgressBarProcessor, StateProcessor, WriterProcessor, \
    WatermarkProcessor

from .classes.dto import Result
from .classes.states import WaitingCenterState
from .processors.accuracy_statistic_processor import AccuracyStatisticProcessor
from .processors.cords_cache_processor import CordsCacheProcessor
from .processors.csv_writer_processor import CsvWriterProcessor
from .processors.drawer_processor import DrawerProcessor
from .processors.tendency_processor import TendencyProcessor


@BehaviorTestFactory.register('Corner')
class CornerExtBehaviorTest(BehaviorTest):
    model_path = os.path.join('behaviour_tests', 'corner_ext', 'models')

    def create(self, model: str, path: str, report_path: str) -> None:
        result = Result()
        model_path = os.path.join(self.model_path, model)
        processors = [
            DataProcessor(DLCLiveDataExtractor(model_path), result),
            AccuracyStatisticProcessor(result),
            CordsCacheProcessor(),
            StateProcessor(WaitingCenterState(), result),
            TendencyProcessor(result),
            WatermarkProcessor(os.path.join('assets', 'logo.png')),
            DrawerProcessor(path, result, show_window=False),
            WriterProcessor(path),
            CsvWriterProcessor(report_path.replace('.csv', 'span.csv'), path, result),
            ProgressBarProcessor(os.path.basename(path)),
        ]
        Process(path, processors).run()

    def watch(self, model: str, path: str) -> None:
        model_path = os.path.join(self.model_path, model)
        result = Result()
        processors = [
            DataProcessor(DLCLiveDataExtractor(model_path), result),
            AccuracyStatisticProcessor(result),
            CordsCacheProcessor(),
            StateProcessor(WaitingCenterState(), result),
            DrawerProcessor(path, result),
        ]
        Process(path, processors).run()
