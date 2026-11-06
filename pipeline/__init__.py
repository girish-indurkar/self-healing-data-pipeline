"""Pipeline package for the self-healing data pipeline."""
try:
    from self_healing_pipeline.pipeline.runner import run_pipeline
except ImportError:
    try:
        from pipeline.runner import run_pipeline
    except ImportError:
        pass

__all__ = ["run_pipeline"]
