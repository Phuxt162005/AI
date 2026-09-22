"""Model and training database schema."""

MODEL_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `models` (
    `model_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `model_type` VARCHAR(100) NOT NULL,
    `framework` VARCHAR(100) NOT NULL DEFAULT '',
    `description` TEXT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`model_id`),
    UNIQUE KEY `uq_models_name` (`name`),
    INDEX `idx_models_status` (`status`)
) ENGINE=InnoDB;
""".strip()


DATASET_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `training_datasets` (
    `dataset_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `version` VARCHAR(100) NOT NULL,
    `storage_reference` TEXT NOT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'active',
    `metadata` JSON NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`dataset_id`),
    UNIQUE KEY `uq_dataset_version` (`name`, `version`)
) ENGINE=InnoDB;
""".strip()


TRAINING_CONFIGURATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `training_configurations` (
    `configuration_id` BIGINT NOT NULL AUTO_INCREMENT,
    `version` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `parameters` JSON NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`configuration_id`),
    UNIQUE KEY `uq_training_configuration_version`
        (`version`)
) ENGINE=InnoDB;
""".strip()


TRAINING_RUN_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `training_runs` (
    `training_run_id` BIGINT NOT NULL AUTO_INCREMENT,
    `dataset_id` BIGINT NOT NULL,
    `configuration_id` BIGINT NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'queued',
    `started_at` TIMESTAMP NULL,
    `finished_at` TIMESTAMP NULL,
    `metrics` JSON NULL,
    `error_message` TEXT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`training_run_id`),

    CONSTRAINT `fk_training_runs_dataset`
        FOREIGN KEY (`dataset_id`)
        REFERENCES `training_datasets` (`dataset_id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT `fk_training_runs_configuration`
        FOREIGN KEY (`configuration_id`)
        REFERENCES `training_configurations`
            (`configuration_id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX `idx_training_runs_dataset`
        (`dataset_id`),

    INDEX `idx_training_runs_configuration`
        (`configuration_id`),

    INDEX `idx_training_runs_status`
        (`status`)
) ENGINE=InnoDB;
""".strip()


MODEL_VERSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `model_versions` (
    `model_version_id` BIGINT NOT NULL AUTO_INCREMENT,
    `model_id` BIGINT NOT NULL,
    `version` VARCHAR(100) NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'development',
    `training_run_id` BIGINT NULL,
    `artifact_reference` TEXT NULL,
    `parameters` JSON NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`model_version_id`),

    CONSTRAINT `fk_model_versions_model`
        FOREIGN KEY (`model_id`)
        REFERENCES `models` (`model_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_model_versions_training_run`
        FOREIGN KEY (`training_run_id`)
        REFERENCES `training_runs`
            (`training_run_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_model_version`
        (`model_id`, `version`),

    INDEX `idx_model_versions_model`
        (`model_id`),

    INDEX `idx_model_versions_status`
        (`status`)
) ENGINE=InnoDB;
""".strip()


EVALUATION_RESULT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `evaluation_results` (
    `evaluation_id` BIGINT NOT NULL AUTO_INCREMENT,
    `model_version_id` BIGINT NOT NULL,
    `dataset_id` BIGINT NULL,
    `metric_name` VARCHAR(100) NOT NULL,
    `metric_value` DOUBLE NOT NULL,
    `details` JSON NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`evaluation_id`),

    CONSTRAINT `fk_evaluation_model_version`
        FOREIGN KEY (`model_version_id`)
        REFERENCES `model_versions`
            (`model_version_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT `fk_evaluation_dataset`
        FOREIGN KEY (`dataset_id`)
        REFERENCES `training_datasets`
            (`dataset_id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    INDEX `idx_evaluation_model_version`
        (`model_version_id`)
) ENGINE=InnoDB;
""".strip()


MODEL_REGISTRY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `model_registry` (
    `registry_id` BIGINT NOT NULL AUTO_INCREMENT,
    `model_version_id` BIGINT NOT NULL,
    `environment` VARCHAR(64) NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'registered',
    `registered_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`registry_id`),

    CONSTRAINT `fk_registry_model_version`
        FOREIGN KEY (`model_version_id`)
        REFERENCES `model_versions`
            (`model_version_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE KEY `uq_registry_model_version_environment`
        (`model_version_id`, `environment`),

    INDEX `idx_registry_environment`
        (`environment`),

    INDEX `idx_registry_status`
        (`status`)
) ENGINE=InnoDB;
""".strip()


MODEL_TABLES_UP_SQL = "\n\n".join(
    [
        MODEL_TABLE_SQL,
        DATASET_TABLE_SQL,
        TRAINING_CONFIGURATION_TABLE_SQL,
        TRAINING_RUN_TABLE_SQL,
        MODEL_VERSION_TABLE_SQL,
        EVALUATION_RESULT_TABLE_SQL,
        MODEL_REGISTRY_TABLE_SQL,
    ]
)


MODEL_TABLES_DOWN_SQL = """
DROP TABLE IF EXISTS `model_registry`;
DROP TABLE IF EXISTS `evaluation_results`;
DROP TABLE IF EXISTS `model_versions`;
DROP TABLE IF EXISTS `training_runs`;
DROP TABLE IF EXISTS `training_configurations`;
DROP TABLE IF EXISTS `training_datasets`;
DROP TABLE IF EXISTS `models`;
""".strip()