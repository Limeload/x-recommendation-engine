"""
A/B Testing Framework
Compare ranking outcomes under different algorithmic configurations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import json

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


class ExperimentStatus(str, Enum):
    """Experiment lifecycle status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ExperimentConfig(BaseModel):
    """Configuration for an A/B test"""
    name: str
    description: Optional[str] = None
    control_weights: Dict[str, float]
    treatment_weights: Dict[str, float]
    split_ratio: float = 0.5  # % users in treatment group


class Experiment(BaseModel):
    """An A/B test experiment"""
    experiment_id: str
    name: str
    description: Optional[str]
    status: ExperimentStatus
    control_weights: Dict[str, float]
    treatment_weights: Dict[str, float]
    split_ratio: float
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class ExperimentResults(BaseModel):
    """Results from an A/B test"""
    experiment_id: str
    name: str
    control_metrics: Dict
    treatment_metrics: Dict
    statistical_significance: float
    winner: Optional[str]  # "control", "treatment", or None


class ExperimentManager:
    """Manages A/B testing experiments"""

    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.experiment_counter = 0
        self.results: Dict[str, ExperimentResults] = {}

    def create_experiment(
        self,
        name: str,
        description: str,
        control_weights: Dict[str, float],
        treatment_weights: Dict[str, float],
        split_ratio: float = 0.5
    ) -> Experiment:
        """Create a new experiment"""
        exp_id = f"exp_{self.experiment_counter}"
        self.experiment_counter += 1

        experiment = Experiment(
            experiment_id=exp_id,
            name=name,
            description=description,
            status=ExperimentStatus.DRAFT,
            control_weights=control_weights,
            treatment_weights=treatment_weights,
            split_ratio=split_ratio,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.experiments[exp_id] = experiment
        return experiment

    def start_experiment(self, experiment_id: str) -> Experiment:
        """Start an experiment"""
        if experiment_id not in self.experiments:
            return None

        exp = self.experiments[experiment_id]
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.utcnow()
        exp.updated_at = datetime.utcnow()
        return exp

    def end_experiment(self, experiment_id: str) -> Experiment:
        """End an experiment"""
        if experiment_id not in self.experiments:
            return None

        exp = self.experiments[experiment_id]
        exp.status = ExperimentStatus.COMPLETED
        exp.ended_at = datetime.utcnow()
        exp.updated_at = datetime.utcnow()
        return exp

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID"""
        return self.experiments.get(experiment_id)

    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Experiment]:
        """List experiments, optionally filtered by status"""
        exps = list(self.experiments.values())

        if status:
            exps = [e for e in exps if e.status == status]

        exps.sort(key=lambda e: e.created_at, reverse=True)
        return exps

    def record_experiment_results(
        self,
        experiment_id: str,
        control_metrics: Dict,
        treatment_metrics: Dict
    ) -> ExperimentResults:
        """Record results from an experiment"""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return None

        # Simple statistical test: compare key metrics
        control_engagement = control_metrics.get("average_engagement", 0)
        treatment_engagement = treatment_metrics.get("average_engagement", 0)

        # Determine winner (simplified - in production use proper statistical tests)
        if treatment_engagement > control_engagement * 1.05:  # 5% threshold
            winner = "treatment"
            significance = min((treatment_engagement / control_engagement - 1) * 100, 100)
        elif control_engagement > treatment_engagement * 1.05:
            winner = "control"
            significance = min((control_engagement / treatment_engagement - 1) * 100, 100)
        else:
            winner = None
            significance = 0

        results = ExperimentResults(
            experiment_id=experiment_id,
            name=exp.name,
            control_metrics=control_metrics,
            treatment_metrics=treatment_metrics,
            statistical_significance=significance,
            winner=winner
        )

        self.results[experiment_id] = results
        return results


# Global experiment manager
experiment_manager = ExperimentManager()


def init_experiment_manager(manager: ExperimentManager):
    """Initialize the global experiment manager"""
    global experiment_manager
    experiment_manager = manager


@router.post("/create")
async def create_experiment(config: ExperimentConfig) -> Experiment:
    """
    Create a new A/B test experiment.

    Args:
        config: Experiment configuration

    Returns:
        Created experiment

    Example:
        ```
        POST /api/experiments/create
        {
            "name": "Recency vs Popularity",
            "description": "Test if recency boost increases engagement",
            "control_weights": {
                "recency": 0.2,
                "popularity": 0.25,
                "quality": 0.2,
                "topic_relevance": 0.25,
                "diversity": 0.1
            },
            "treatment_weights": {
                "recency": 0.5,
                "popularity": 0.15,
                "quality": 0.15,
                "topic_relevance": 0.15,
                "diversity": 0.05
            },
            "split_ratio": 0.5
        }
        ```
    """
    experiment = experiment_manager.create_experiment(
        name=config.name,
        description=config.description,
        control_weights=config.control_weights,
        treatment_weights=config.treatment_weights,
        split_ratio=config.split_ratio
    )
    return experiment


@router.post("/{experiment_id}/start")
async def start_experiment(experiment_id: str) -> Experiment:
    """
    Start an experiment.

    Args:
        experiment_id: Experiment to start

    Returns:
        Updated experiment

    Example:
        ```
        POST /api/experiments/exp_0/start
        ```
    """
    experiment = experiment_manager.start_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.post("/{experiment_id}/end")
async def end_experiment(experiment_id: str) -> Experiment:
    """
    End an experiment.

    Args:
        experiment_id: Experiment to end

    Returns:
        Updated experiment

    Example:
        ```
        POST /api/experiments/exp_0/end
        ```
    """
    experiment = experiment_manager.end_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str) -> Experiment:
    """
    Get experiment details.

    Args:
        experiment_id: Experiment ID

    Returns:
        Experiment details

    Example:
        ```
        GET /api/experiments/exp_0
        ```
    """
    experiment = experiment_manager.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.get("/")
async def list_experiments(status: Optional[ExperimentStatus] = None) -> List[Experiment]:
    """
    List experiments.

    Args:
        status: Optional filter by status

    Returns:
        List of experiments

    Example:
        ```
        GET /api/experiments/
        GET /api/experiments/?status=running
        ```
    """
    return experiment_manager.list_experiments(status)


@router.post("/{experiment_id}/results")
async def record_results(
    experiment_id: str,
    control_metrics: Dict,
    treatment_metrics: Dict
) -> ExperimentResults:
    """
    Record results from an experiment.

    Args:
        experiment_id: Experiment ID
        control_metrics: Control group metrics
        treatment_metrics: Treatment group metrics

    Returns:
        Experiment results with statistical analysis

    Example:
        ```
        POST /api/experiments/exp_0/results
        {
            "control_metrics": {
                "average_engagement": 5.2,
                "diversity_index": 0.65,
                "average_recency_hours": 2.3
            },
            "treatment_metrics": {
                "average_engagement": 5.8,
                "diversity_index": 0.62,
                "average_recency_hours": 1.5
            }
        }
        ```
    """
    results = experiment_manager.record_experiment_results(
        experiment_id,
        control_metrics,
        treatment_metrics
    )

    if not results:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return results


@router.get("/{experiment_id}/results")
async def get_results(experiment_id: str) -> ExperimentResults:
    """
    Get results from a completed experiment.

    Args:
        experiment_id: Experiment ID

    Returns:
        Experiment results

    Example:
        ```
        GET /api/experiments/exp_0/results
        ```
    """
    if experiment_id not in experiment_manager.results:
        raise HTTPException(status_code=404, detail="Results not found for this experiment")

    return experiment_manager.results[experiment_id]


class ExperimentTemplate(BaseModel):
    """Pre-defined experiment template"""
    name: str
    description: str
    control_weights: Dict[str, float]
    treatment_weights: Dict[str, float]


# Pre-defined templates for common tests
EXPERIMENT_TEMPLATES = {
    "recency_boost": ExperimentTemplate(
        name="Recency Boost Test",
        description="Test if increasing recency weight increases freshness and engagement",
        control_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1
        },
        treatment_weights={
            "recency": 0.5,
            "popularity": 0.15,
            "quality": 0.15,
            "topic_relevance": 0.15,
            "diversity": 0.05
        }
    ),
    "popularity_boost": ExperimentTemplate(
        name="Popularity Focus Test",
        description="Test if emphasizing popularity increases engagement at cost of diversity",
        control_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1
        },
        treatment_weights={
            "recency": 0.1,
            "popularity": 0.5,
            "quality": 0.15,
            "topic_relevance": 0.15,
            "diversity": 0.1
        }
    ),
    "quality_focus": ExperimentTemplate(
        name="Quality Focus Test",
        description="Test if emphasizing quality reduces spam but may reduce engagement",
        control_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1
        },
        treatment_weights={
            "recency": 0.1,
            "popularity": 0.15,
            "quality": 0.5,
            "topic_relevance": 0.15,
            "diversity": 0.1
        }
    ),
    "diversity_focus": ExperimentTemplate(
        name="Diversity Focus Test",
        description="Test if increasing diversity reduces filter bubbles",
        control_weights={
            "recency": 0.2,
            "popularity": 0.25,
            "quality": 0.2,
            "topic_relevance": 0.25,
            "diversity": 0.1
        },
        treatment_weights={
            "recency": 0.15,
            "popularity": 0.15,
            "quality": 0.15,
            "topic_relevance": 0.15,
            "diversity": 0.4
        }
    )
}


@router.get("/templates/list")
async def list_experiment_templates() -> Dict[str, ExperimentTemplate]:
    """
    Get pre-defined experiment templates.

    Returns:
        Dictionary of templates

    Example:
        ```
        GET /api/experiments/templates/list
        ```
    """
    return EXPERIMENT_TEMPLATES


@router.post("/templates/{template_key}/create")
async def create_from_template(template_key: str) -> Experiment:
    """
    Create an experiment from a template.

    Args:
        template_key: Template key (e.g., "recency_boost")

    Returns:
        Created experiment

    Example:
        ```
        POST /api/experiments/templates/recency_boost/create
        ```
    """
    if template_key not in EXPERIMENT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")

    template = EXPERIMENT_TEMPLATES[template_key]

    experiment = experiment_manager.create_experiment(
        name=template.name,
        description=template.description,
        control_weights=template.control_weights,
        treatment_weights=template.treatment_weights
    )

    return experiment
