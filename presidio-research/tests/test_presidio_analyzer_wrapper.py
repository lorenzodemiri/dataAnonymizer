import pytest

from presidio_evaluator import InputSample, Span
from presidio_evaluator.data_generator import read_synth_dataset
from presidio_evaluator.evaluation import Evaluator
from presidio_evaluator.models.presidio_analyzer_wrapper import PresidioAnalyzerWrapper


class GeneratedTextTestCase:
    def __init__(self, test_name, test_input, acceptance_threshold, marks):
        self.test_name = test_name
        self.test_input = test_input
        self.acceptance_threshold = acceptance_threshold
        self.marks = marks

    def to_pytest_param(self):
        return pytest.param(
            self.test_input,
            self.acceptance_threshold,
            id=self.test_name,
            marks=self.marks,
        )


# generated-text test cases
analyzer_test_generate_text_testdata = [
    # small set fixture which expects all results.
    GeneratedTextTestCase(
        test_name="small-set",
        test_input="{}/data/generated_small.txt",
        acceptance_threshold=0.3,
        marks=pytest.mark.none,
    )
]


def test_analyzer_simple_input():
    model = PresidioAnalyzerWrapper(entities_to_keep=["PERSON"])
    sample = InputSample(
        full_text="My name is Mike",
        masked="My name is [PERSON]",
        spans=[Span("PERSON", "Mike", 10, 14)],
        create_tags_from_span=True,
    )

    prediction = model.predict(sample)
    evaluator = Evaluator(model=model)

    evaluated = evaluator.evaluate_sample(sample, prediction)
    metrics = evaluator.calculate_score([evaluated])

    assert metrics.pii_precision == 1
    assert metrics.pii_recall == 1


# analyzer tests on generated data
@pytest.mark.parametrize(
    "test_input,acceptance_threshold",
    [testcase.to_pytest_param() for testcase in analyzer_test_generate_text_testdata],
)
def test_analyzer_with_generated_text(test_input, acceptance_threshold):
    """
        Test analyzer with a generated dataset text file
        :param test_input: input text file location
        :param acceptance_threshold: minimim precision/recall
         allowed for tests to pass
    """
    # read test input from generated file

    import os

    dir_path = os.path.dirname(os.path.realpath(__file__))
    input_samples = read_synth_dataset(test_input.format(dir_path))

    updated_samples = Evaluator.align_entity_types(
        input_samples=input_samples, entities_mapping=PresidioAnalyzerWrapper.presidio_entities_map
    )

    analyzer = PresidioAnalyzerWrapper()
    evaluator = Evaluator(model=analyzer)
    evaluated_samples = evaluator.evaluate_all(updated_samples)
    scores = evaluator.calculate_score(evaluation_results=evaluated_samples)

    assert acceptance_threshold <= scores.pii_precision
    assert acceptance_threshold <= scores.pii_recall
