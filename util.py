from pprint import pprint
import sys
from pathlib import Path


LINE_NO = '_i'
BATCH_NO = '_b'

BOTH = 'both'
TEST = 'test'
PUZZLE = 'puzzle'

LINE = 'line'
BATCH = 'batch'
FILE = 'file'


def read_lines_from_file(
    filename, process_line, state=None, strip=True, post_process=None
):
    if state is None:
        state = {}
    state[LINE_NO] = 0
    with open(filename) as f:
        for (i, line) in enumerate(f.readlines()):
            state[LINE_NO] = i
            process_line(line if not strip else line.rstrip(), state)

    if post_process is not None:
        post_process(state)

    return {key: value for key, value in state.items() if not key.startswith("_")}


def read_batches_from_file(
    filename, process_batch, state=None, strip=True, post_process=None
):
    if state is None:
        state = {}
    state[BATCH_NO] = 0
    batch = []
    with open(filename) as f:
        for line in f.readlines():
            if not line.rstrip():
                process_batch(batch, state)
                batch = []
                state[BATCH_NO] += 1
            else:
                batch.append(line if not strip else line.rstrip())

    process_batch(batch, state)
    if post_process is not None:
        post_process(state)

    return {key: value for key, value in state.items() if not key.startswith("_")}


class Solver:
    def __init__(self, unit, file, *, strip=True, debug=False):
        self._unit = unit
        self._file = file
        self._strip = strip
        self._debug = debug
        self._line_count = 0
        self._batch_count = 0
        self._print_args = []

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def process_line(self, line):
        pass

    def process_batch(self, batch):
        pass

    def process_file(self, file):
        pass

    def process_result(self):
        pass

    def solve(self):
        self.pre_process()
        if self._unit == LINE:
            self.solve_lines()
        elif self._unit == BATCH:
            self.solve_batches()
        else:
            self.solve_file()
        self.post_process()

    def solve_lines(self):
        self._line_count = 0
        with self._file.open() as f:
            for (i, line) in enumerate(f.readlines()):
                self._line_count = i
                self.process_line(line if not self._strip else line.rstrip())

    def solve_batches(self):
        self._batch_count = 0

        batch = []
        with self._file.open() as f:
            for line in f.readlines():
                if not line.rstrip():
                    self.process_batch(batch)
                    batch = []
                    self._batch_count += 1
                else:
                    batch.append(line if not self._strip else line.rstrip())

        self.process_batch(batch)

    def solve_file(self):
        with self._file.open() as f:
            self.process_file(f.readlines())

    def print(self):
        self.process_result()

        if not self._print_args:
            result_state = {
                key: value
                for key, value in vars(self).items()
                if self._debug or not key.startswith("_")
            }
        else:
            result_state = {
                key: getattr(self, key)
                for key in self._print_args
                if hasattr(self, key)
            }

        if len(result_state) == 1:
            pprint(result_state.popitem()[1])
        else:
            pprint(result_state)


class Tester:
    def __init__(
        self,
        solverClass,
        unit,
        mode=BOTH,
        **kwargs,
    ):
        self.solverClass = solverClass
        self.unit = unit
        self.mode = mode
        self.kwargs = kwargs
        self.file = sys.argv[0].removesuffix('.py')

    def test(self):
        files = []
        if self.mode in [BOTH, TEST]:
            files.append(self.file + '-example.input')
        if self.mode in [BOTH, PUZZLE]:
            files.append(self.file + '.input')

        for file in files:
            filepath = Path(file)
            if filepath.exists():
                print(f'Solver: {self.solverClass.__name__}\t Input: {filepath.name}')
                solver = self.solverClass(self.unit, filepath, **self.kwargs)
                solver.solve()
                solver.print()
                print()
