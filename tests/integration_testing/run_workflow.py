import yappi
from pathlib import Path
import io
import sys
import logging

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from scout import ecm_prep  # noqa: E402
from scout.ecm_prep_args import ecm_args  # noqa: E402
from scout import run  # noqa: E402

yappi.set_clock_type("cpu")
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


def run_workflow():
    results_dir = Path(__file__).parent / "results"

    # Run ecm_prep.py
    yappi.start()
    opts = ecm_args(["--alt_regions_option", "EMM"])
    ecm_prep.main(opts)
    stats = get_stats()
    yappi.stop()
    write_profile_stats(stats, results_dir / "profile_ecm_prep.csv")

    # Run run.py
    yappi.start()
    opts = run.parse_args([])
    run.main(opts)
    stats = get_stats()
    yappi.stop()
    write_profile_stats(stats, results_dir / "profile_run.csv")


def get_stats():
    stats = yappi.get_func_stats()
    stats = yappi.convert2pstats(stats)
    return stats


def write_profile_stats(stats, filepath):
    s = io.StringIO()
    stats.stream = s
    stats.strip_dirs().sort_stats("tottime").print_stats()
    result = s.getvalue()

    # Parse stats and write to csv
    top_data, result = result.split("ncalls")
    top_data = "\n".join([line.strip() for line in top_data.split("\n")])
    result = "ncalls" + result
    result = "\n".join([",".join(line.rstrip().split(None, 5)) for line in result.split("\n")])
    result_out = top_data + result

    f = open(filepath, "w")
    f.write(result_out)
    f.close()
    logger.info(f"Wrote profiler stats to {filepath}")


if __name__ == "__main__":
    run_workflow()
