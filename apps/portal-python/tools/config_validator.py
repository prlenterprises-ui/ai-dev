"""Configuration Validator

Validates YAML configuration files for job search settings.
Adapted from AIHawk's ConfigValidator with improvements.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Set
import yaml


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigValidator:
    """Validates job search configuration files."""
    
    # Email validation regex
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    # Valid experience levels
    EXPERIENCE_LEVELS = [
        "internship",
        "entry",
        "associate",
        "mid_senior_level",
        "director",
        "executive",
    ]
    
    # Valid job types
    JOB_TYPES = [
        "full_time",
        "contract",
        "part_time",
        "temporary",
        "internship",
        "other",
        "volunteer",
    ]
    
    # Valid date filters
    DATE_FILTERS = ["all_time", "month", "week", "24_hours"]
    
    # Approved distance values (in miles)
    APPROVED_DISTANCES: Set[int] = {0, 5, 10, 25, 50, 100}
    
    # Required configuration keys
    REQUIRED_CONFIG_KEYS = {
        "remote": bool,
        "experience_level": dict,
        "job_types": dict,
        "date": dict,
        "positions": list,
        "locations": list,
        "distance": int,
    }
    
    # Optional configuration keys
    OPTIONAL_CONFIG_KEYS = {
        "location_blacklist": list,
        "company_blacklist": list,
        "title_blacklist": list,
        "min_salary": int,
        "max_salary": int,
    }
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        return bool(ConfigValidator.EMAIL_REGEX.match(email))
    
    @staticmethod
    def load_yaml(yaml_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Parsed YAML data
            
        Raises:
            ConfigError: If file not found or invalid YAML
        """
        try:
            with open(yaml_path, "r") as stream:
                return yaml.safe_load(stream) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Error reading YAML file {yaml_path}: {exc}")
        except FileNotFoundError:
            raise ConfigError(f"YAML file not found: {yaml_path}")
    
    @classmethod
    def validate_config(cls, config_yaml_path: Path) -> Dict[str, Any]:
        """Validate main configuration YAML file.
        
        Args:
            config_yaml_path: Path to config YAML
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ConfigError: If configuration is invalid
        """
        parameters = cls.load_yaml(config_yaml_path)
        
        # Check for required keys and their types
        for key, expected_type in cls.REQUIRED_CONFIG_KEYS.items():
            if key not in parameters:
                raise ConfigError(
                    f"Missing required key '{key}' in {config_yaml_path}"
                )
            elif not isinstance(parameters[key], expected_type):
                raise ConfigError(
                    f"Invalid type for key '{key}' in {config_yaml_path}. "
                    f"Expected {expected_type.__name__}."
                )
        
        # Set defaults for optional keys
        for key, expected_type in cls.OPTIONAL_CONFIG_KEYS.items():
            if key not in parameters:
                if expected_type == list:
                    parameters[key] = []
                elif expected_type == int:
                    parameters[key] = None
            elif parameters[key] is None and expected_type == list:
                parameters[key] = []
        
        # Validate specific fields
        cls._validate_experience_levels(
            parameters["experience_level"], config_yaml_path
        )
        cls._validate_job_types(parameters["job_types"], config_yaml_path)
        cls._validate_date_filters(parameters["date"], config_yaml_path)
        cls._validate_list_of_strings(
            parameters, ["positions", "locations"], config_yaml_path
        )
        cls._validate_distance(parameters["distance"], config_yaml_path)
        cls._validate_blacklists(parameters, config_yaml_path)
        
        if "min_salary" in parameters and "max_salary" in parameters:
            cls._validate_salary_range(
                parameters.get("min_salary"),
                parameters.get("max_salary"),
                config_yaml_path
            )
        
        return parameters
    
    @classmethod
    def _validate_experience_levels(cls, experience_levels: Dict[str, bool],
                                   config_path: Path):
        """Validate experience levels are booleans.
        
        Args:
            experience_levels: Experience level settings
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid experience levels
        """
        for level in cls.EXPERIENCE_LEVELS:
            if level in experience_levels:
                if not isinstance(experience_levels[level], bool):
                    raise ConfigError(
                        f"Experience level '{level}' must be a boolean in {config_path}"
                    )
    
    @classmethod
    def _validate_job_types(cls, job_types: Dict[str, bool], config_path: Path):
        """Validate job types are booleans.
        
        Args:
            job_types: Job type settings
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid job types
        """
        for job_type in cls.JOB_TYPES:
            if job_type in job_types:
                if not isinstance(job_types[job_type], bool):
                    raise ConfigError(
                        f"Job type '{job_type}' must be a boolean in {config_path}"
                    )
    
    @classmethod
    def _validate_date_filters(cls, date_filters: Dict[str, bool],
                              config_path: Path):
        """Validate date filters are booleans.
        
        Args:
            date_filters: Date filter settings
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid date filters
        """
        for date_filter in cls.DATE_FILTERS:
            if date_filter in date_filters:
                if not isinstance(date_filters[date_filter], bool):
                    raise ConfigError(
                        f"Date filter '{date_filter}' must be a boolean in {config_path}"
                    )
    
    @classmethod
    def _validate_list_of_strings(cls, parameters: Dict[str, Any],
                                  keys: List[str], config_path: Path):
        """Validate specified keys are lists of strings.
        
        Args:
            parameters: Configuration parameters
            keys: Keys to validate
            config_path: Path to config file
            
        Raises:
            ConfigError: If not lists of strings
        """
        for key in keys:
            if key in parameters:
                if not all(isinstance(item, str) for item in parameters[key]):
                    raise ConfigError(
                        f"'{key}' must be a list of strings in {config_path}"
                    )
    
    @classmethod
    def _validate_distance(cls, distance: int, config_path: Path):
        """Validate distance value.
        
        Args:
            distance: Distance value in miles
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid distance
        """
        if distance not in cls.APPROVED_DISTANCES:
            raise ConfigError(
                f"Invalid distance '{distance}' in {config_path}. "
                f"Must be one of {cls.APPROVED_DISTANCES}"
            )
    
    @classmethod
    def _validate_blacklists(cls, parameters: Dict[str, Any], config_path: Path):
        """Validate blacklist fields.
        
        Args:
            parameters: Configuration parameters
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid blacklists
        """
        blacklist_keys = [
            "company_blacklist",
            "title_blacklist",
            "location_blacklist"
        ]
        cls._validate_list_of_strings(parameters, blacklist_keys, config_path)
    
    @classmethod
    def _validate_salary_range(cls, min_salary: int, max_salary: int,
                              config_path: Path):
        """Validate salary range.
        
        Args:
            min_salary: Minimum salary
            max_salary: Maximum salary
            config_path: Path to config file
            
        Raises:
            ConfigError: If invalid salary range
        """
        if min_salary and max_salary:
            if min_salary > max_salary:
                raise ConfigError(
                    f"min_salary ({min_salary}) cannot be greater than "
                    f"max_salary ({max_salary}) in {config_path}"
                )


# CLI interface
def main():
    """CLI interface for config validation."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Validate job search configuration files'
    )
    parser.add_argument('config_file', help='Path to configuration YAML file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed validation results')
    
    args = parser.parse_args()
    
    config_path = Path(args.config_file)
    
    if not config_path.exists():
        print(f"❌ Error: File not found: {config_path}")
        sys.exit(1)
    
    try:
        print(f"🔍 Validating configuration: {config_path}")
        config = ConfigValidator.validate_config(config_path)
        
        print("✅ Configuration is valid!\n")
        
        if args.verbose:
            print("Configuration summary:")
            print(f"  Remote jobs: {config['remote']}")
            print(f"  Positions: {len(config['positions'])} roles")
            print(f"  Locations: {len(config['locations'])} locations")
            print(f"  Distance: {config['distance']} miles")
            
            exp_enabled = [k for k, v in config['experience_level'].items() if v]
            if exp_enabled:
                print(f"  Experience levels: {', '.join(exp_enabled)}")
            
            job_types_enabled = [k for k, v in config['job_types'].items() if v]
            if job_types_enabled:
                print(f"  Job types: {', '.join(job_types_enabled)}")
            
            if config.get('company_blacklist'):
                print(f"  Company blacklist: {len(config['company_blacklist'])} companies")
            if config.get('title_blacklist'):
                print(f"  Title blacklist: {len(config['title_blacklist'])} keywords")
        
        sys.exit(0)
        
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
