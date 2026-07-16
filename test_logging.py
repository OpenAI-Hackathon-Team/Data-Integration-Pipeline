from pipeline_logs import run_with_logging
from etl.load import main as run_etl

run_with_logging(run_etl, run_label="real_etl_run")