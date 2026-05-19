import os
from pathlib import Path
import concurrent.futures

def _execute_parallel_task(task):
    """
    Must live at the top level of the module so workers can see it.
    Unwraps and executes the frozen task object.
    """
    if callable(task):
        return task()
    
    # Optional fallback: also supports raw tuples like (func, args_tuple, kwargs_dict)
    func, args, kwargs = task
    return func(*args, **kwargs)


def python_parallel(cfg, title=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            original_cwd = os.getcwd()
            try:
                # 1. Setup working directory
                Path(cfg.common.working_dir).mkdir(parents=True, exist_ok=True)
                os.chdir(cfg.common.working_dir)

                # 2. MATCHING GNU_PARALLEL: Generate the list of prepared tasks
                tasks = func(*args, **kwargs)

                logger = cfg.common.logger
                n_jobs = int(cfg.common.n_jobs)
                local_title = title if title is not None else ""
                
                logger.info(f"Running: Python Parallel {local_title} for {len(tasks)} jobs")

                results = [None] * len(tasks)
                
                # 3. Execute the frozen tasks in parallel
                with concurrent.futures.ProcessPoolExecutor(max_workers=n_jobs) as executor:
                    future_to_index = {}
                    
                    for i, task in enumerate(tasks):
                        # Ship the task to our top-level executor helper
                        future = executor.submit(_execute_parallel_task, task)
                        future_to_index[future] = i

                    # 4. Gather results in original order
                    for future in concurrent.futures.as_completed(future_to_index):
                        index = future_to_index[future]
                        try:
                            results[index] = future.result()
                        except Exception as e:
                            logger.error(f"Task {index} failed with error: {e}")
                            raise

                return results

            finally:
                # 5. Cleanup CWD
                os.chdir(original_cwd)

        return wrapper
    return decorator